"""
classifier.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("Classifier", "ClfWriter", "ClfDataModel")

import h5py
import numpy as np
from collections import OrderedDict

from PyQt4 import QtGui

from annot.config import AtConfig
from annot.pattern import Factory
from annot.classifiers.itemclass import UnClassified
from annot.preprocessor import PreProcessor
from annot.hdfio.readercore import HdfFile


class ClfDataModel(object):
    """Data model to save a Support Vector classifier to hdf5.

    It defines attribute names, group names (paths) and constants.
    """

    # constants, strings strings should be the import path of
    # corresponding module
    OneClassSvm = "sklearn.svm.OneClassSvm"
    SupportVectorClassifier = "sklearn.svm.SVC"

    # attribute keys
    NAME = "name"
    LIB = "library"
    VERSION = "version"
    FEATURE_SELECTION = "feature_selection"
    DESCRIPTION = "description"

    def __init__(self, name):
        self.name = name
        self.path = "/classifiers/%s" %name
        self.parameters = "%s/parameters" %self.path
        self.training_set = "%s/training_set" %self.path
        self.classdef = "%s/class_definition" %self.path
        self.normalization = "%s/normalization" %self.path
        self.sample_info = "%s/sample_info" %self.path

        self.annotations = "%s/annotations" %self.path
        self.confmatrix = "%s/confusion_matrix" %self.path


class ClfWriter(object):

    def __init__(self, file_):
        super(ClfWriter, self).__init__()

        self._compression = AtConfig().compression
        self._copts = AtConfig().compression_opts

        if isinstance(file_, HdfFile):
            self.h5f = file_
        elif isinstance(file_, basestring):
            self.h5f = h5py.File(file_, HdfFile.READWRITECREATE)

    def flush(self):
        self.h5f.flush()

    def saveTrainingSet(self, features, feature_names):
        dtype = [(str(fn), np.float32) for fn in feature_names]
        f2 = features.copy().astype(np.float32).view(dtype)
        dset = self.h5f.create_dataset(self.dmodel.training_set,
                                       data=f2,
                                       compression=self._compression,
                                       compression_opts=self._copts)

    def saveClassDef(self, classes, classifier_params=None):

        dt = [("name", "S64"), ("label", int), ("color", "S7")]
        classdef = np.empty(len(classes, ), dtype=dt)

        for i, class_ in enumerate(classes.itervalues()):
            classdef[i] = (class_.name, class_.label, class_.color.name())

        dset = self.h5f.create_dataset(self.dmodel.classdef,
                                       data=classdef,
                                       compression=self._compression,
                                       compression_opts=self._copts)

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

        dset = self.h5f.create_dataset(self.dmodel.normalization, data=norm,
                                       compression=self._compression,
                                       compression_opts=self._copts)

    def saveSampleInfo(self, sample_info):
        dset = self.h5f.create_dataset(
            self.dmodel.sample_info, data=sample_info,
            compression=self._compression, compression_opts=self._copts)


# TODO need design pattern QFactory (which segfautlts right now!)
class Classifier(object):
    """Parent factory for all classifier classes."""

    __metaclass__ = Factory

    def __init__(self):
        super(Classifier, self).__init__()
        self._pp = None # setup preprocessor in the train method
        self.model = None
        self._clf = None
        self._actions = list()
        self._classes = OrderedDict()

    def setParameters(self, *args, **kw):
        raise NotImplementedError

    def setupPreProcessor(self, features):
        self._pp = PreProcessor(features)

    def normalize(self, features):
        return self._pp(features)

    @property
    def actions(self):
        return self._actions

    @property
    def classes(self):
        return self._classes

    def classByName(self, name):
        for class_ in self.classes.itervalues():
            if class_.name == name:
                return class_

        raise RuntimeError("No classes named %s" %name)

    def setClasses(self, classes, parent, panel):
        """Update the dictionary of the class definition and the list of
        the context menu actions."""

        self._classes.clear()
        self._classes.update(classes)
        self.createActions(parent, panel)

    def createActions(self, parent, panel):
        """Create context menu actions according to the class definition."""

        self._actions = list()
        for name in self._classes.keys():
            self.actions.append(
                QtGui.QAction( "add to %s" %name, parent,
                    triggered=lambda: panel.addAnnotation(name)))

    @classmethod
    def classifiers(cls):
        return cls._classes.keys()

    def parameterWidget(self, parent):
        return QtGui.QWidget(self)

    def train(self, features):
        raise NotImplementedError

    def predict(self, features):
        return [UnClassified]*features.shape[0]

    def saveToHdf(self, file_, feature_names):
        raise NotImplementedError
