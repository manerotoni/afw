"""
ocsvm.py

Implementation of a one class support vector machine

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("OneClassSvm", )


import h5py
import sklearn
import sklearn.svm
import numpy as np
from PyQt4 import QtGui

from annot.config import AtConfig
from annot.hdfio.readercore import HdfFile
from annot.hdfio.readercore import HdfError
from annot.preprocessor import PreProcessor
from annot.gui.sidebar.models import AtOneClassSvmItemModel
from .itemclass import ItemClass
from .classifiers import Classifier


class OcSvmDataModel(object):
    """Data model to save one class svm to hdf5."""

    NAME = "name"
    LIB = "library"
    FEATURE_SELECTION = "feature_selection"
    DESCRIPTION = "description"


    def __init__(self, name):

        self.name = name
        self.path = "/classifiers/%s" %name
        self.parameters = "%s/parameters" %self.path
        self.training_set = "%s/training_set" %self.path
        self.classdef = "%s/class_definition" %self.path
        self.normalization = "%s/normalization" %self.path


class OcSvmWriter(object):

    def __init__(self, name, file_, description=None, remove_existing=False):

        assert isinstance(remove_existing, bool)

        self.dmodel = OcSvmDataModel(name)

        if isinstance(file_, HdfFile):
            self.h5f = file_
        elif isinstance(file_, basestring):

            self.h5f = h5py.File(file_, HdfFile.READWRITECREATE)

        if remove_existing:
            try:
                del self.h5f[self.dmodel.path]
            except KeyError:
                pass

        try:
            grp = self.h5f.create_group(self.dmodel.path)
        except ValueError as e:
            raise HdfError("Classifer with name %s exists already"
                           %name + str(e))

        grp.attrs[self.dmodel.NAME] = "one class support vector machine"
        grp.attrs[self.dmodel.LIB] = "sklearn-%s" %sklearn.__version__

        if description is not None:
            grp.attrs[self.dmodel.DESCRIPTION] = description

    def saveTrainingSet(self, features, feature_names):

        dtype = [(str(fn), np.float32) for fn in feature_names]
        f2 = features.copy().astype(np.float32).view(dtype)

        dset = self.h5f.create_dataset(self.dmodel.training_set, data=f2)

    def saveClassDef(self, classes, classifier_params=None):

        dt = [("name", "S64"), ("label", int), ("color", "S7")]
        classdef = np.empty(len(classes, ), dtype=dt)

        for i, class_ in enumerate(classes.itervalues()):
            classdef[i] = (class_.name, class_.label, class_.color.name())

        dset = self.h5f.create_dataset(self.dmodel.classdef, data=classdef)

        if classifier_params is not None:
            # save classifier parameters
            for k, v in classifier_params.iteritems():
                if v is None:
                    dset.attrs[k] = str(v)
                else:
                    dset.attrs[k] = v

    def saveNormalization(self, preproc):

        dt = [("offset", np.float32), ("scale", np.float32), ("colmask", bool)]
        offset = preproc.mean.astype(np.float32)
        scale = preproc.std.astype(np.float32)
        norm = np.empty( (offset.size, ), dtype=dt)

        for i, line in enumerate(zip(offset, scale, preproc.mask)):
            norm[i] = line

        dset = self.h5f.create_dataset(self.dmodel.normalization, data=norm)


class OcSvmParameterWidget(QtGui.QFrame):

    def __init__(self, parent, *args, **kw):
        super(OcSvmParameterWidget, self).__init__(parent, *args, **kw)

        gbox = QtGui.QGridLayout(self)
        gbox.setContentsMargins(5, 2, 2, 2)
        gbox.setSpacing(1)

        self.nu = QtGui.QDoubleSpinBox(self)
        self.nu.setRange(0.0, 1.0)
        self.nu.setSingleStep(0.05)
        self.nu.setValue(0.01)
        self.nu.setDecimals(5)
        self.nu.valueChanged.connect(parent.predictionInvalid)

        self.gamma = QtGui.QDoubleSpinBox(self)
        self.gamma.setRange(0.0, 100.0)
        self.gamma.setSingleStep(0.01)
        self.gamma.setValue(0.5)
        self.gamma.setDecimals(5)
        self.gamma.valueChanged.connect(parent.predictionInvalid)

        self.estBtn = QtGui.QPushButton("estimate")
        self.estBtn.clicked.connect(parent.estimateParameters)

        self.addBtn = QtGui.QPushButton("add items")
        # one class svm does not need the class name
        func = lambda: parent.addAnnotation(OneClassSvm.INLIER.name)
        self.addBtn.clicked.connect(func)

        self.treeview = QtGui.QTreeView(self)
        self.treeview.activated.connect(parent.onActivated)
        self.treeview.setModel(AtOneClassSvmItemModel())
        self.treeview.setSelectionMode(self.treeview.ContiguousSelection)

        gbox.addWidget(QtGui.QLabel("nu", self.nu), 0, 0)
        gbox.addWidget(self.nu, 0, 1)
        gbox.addWidget(QtGui.QLabel("gamma", self.gamma), 1, 0)
        gbox.addWidget(self.gamma, 1, 1)
        gbox.addWidget(self.estBtn, 1, 2)
        gbox.addWidget(self.addBtn, 2, 2)
        gbox.addWidget(self.treeview, 3, 0, 2, 0)


class OneClassSvm(Classifier):
    """Class for training and parameter tuning of a one class svm."""

    KERNEL = "rbf"
    name = "ocsvm"

    # TODO method to set the item classes
    INLIER = ItemClass("inlier", QtGui.QColor("green"), 1)
    OUTLIER = ItemClass("outlier", QtGui.QColor("red"), -1)

    def __init__(self, *args, **kw):
        super(OneClassSvm, self).__init__(*args, **kw)
        self._pp = None
        self._params = None

    @property
    def classes(self):
        return {self.INLIER.label: self.INLIER,
                self.OUTLIER.label: self.OUTLIER}

    def setClasses(self, *args, **kw):
        raise RuntimeError("OneClassSvm has a static class definition. "
                           "You can not overwrite the class definition.")

    def createActions(self, parent, panel):

        self._actions.append(
            QtGui.QAction( "add to %s" %self.INLIER.name, parent,
                triggered=lambda: panel.addAnnotation(self.INLIER.name)))

    def parameterWidget(self, parent):
        self._params = OcSvmParameterWidget(parent)
        return self._params

    def estimateParameters(self, testdata):

        pp = PreProcessor(testdata)

        # check all gammas from 2^-16 to 2^2
        for gamma in 2**np.linspace(-16, 2, 100):
            clf = sklearn.svm.OneClassSVM(kernel=self.KERNEL, nu=self.nu,
                                          gamma=gamma)
            clf.fit(pp(testdata))
            sv_frac = clf.support_.size/float(pp.nsamples)

            if sv_frac >= AtConfig().max_sv_fraction:
                self._params.gamma.setValue(gamma)
                break

    @property
    def nu(self):
        if not (0.0 < self._params.nu.value() <= 1.0):
            raise ValueError(("parameter nu is invalid. "
                              "It's constrained between 0 an 1"))

        return self._params.nu.value()

    @property
    def gamma(self):
        if self._params.gamma.value() <= 0.0:
            raise ValueError(("parameter gamma is invalid. "
                              "It must be larger than zero."))

        return self._params.gamma.value()

    def train(self, features, *args, **kw):
        self._pp = PreProcessor(features)
        self._clf = sklearn.svm.OneClassSVM(
            nu=self.nu, kernel=self.KERNEL, gamma=self.gamma)
        self._clf.fit(self._pp(features))

    def predict(self, features):
        if self._clf is None:
            return super(OneClassSvm, self).predict(features)
        else:
            predictions = self._clf.predict(self._pp(features))
            return [self.classes[pred] for pred in predictions]

    def saveToHdf(self, name, file_, feature_selection, description,
                  overwrite=False):

        writer = OcSvmWriter(name, file_, description, overwrite)
        writer.saveTrainingSet(self._pp.data, feature_selection.values())
        writer.saveClassDef(self.classes, self._clf.get_params())
        writer.saveNormalization(self._pp)
