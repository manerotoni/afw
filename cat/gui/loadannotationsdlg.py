"""
loadannotationsdlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("LoadAnnotationsDialog", )

import h5py
import numpy as np

from os.path import splitext, expanduser
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox

from cat.classifiers.classifiers import ClfDataModel
from cat.hdfio.trainingset import AtTrainingSetIO
from cat.hdfio.guesser import guessHdfType


class LoadAnnotationsDialog(QtWidgets.QDialog):

    def __init__(self, *args, **kw):
        super(LoadAnnotationsDialog, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        uic.loadUi(uifile, self)

        self.descriptions = dict()
        self.progressBar.hide()

        self.pathBtn.clicked.connect(self.onPathBtn)
        self.classifier_name.currentIndexChanged[str].connect(
            self.onClassifierChanged)

    def onClassifierChanged(self, name):

        try:
            self._description.clear()
            txt = self.descriptions[name]
        except KeyError:
            pass
        else:
            self._description.appendPlainText(txt)

    def onPathBtn(self):

        file_ = QFileDialog.getOpenFileName( \
            self, "Select a config file", expanduser('~'),
            ("hdf5 files (*.hdf5 *.h5 *.he5 *.hdf *.hdf4 *.he2 *.he5 *.ch5;;"
            ";;All files (*.*)"))[0]

        if file_:
            self._path.setText(file_)
            self.path = file_

            try:
                hdf = h5py.File(file_, "r")
                clf_names = hdf['classifiers'].keys()
            except KeyError as e:
                QtGui.QMessageBox.critical(self, "Error",
                                           "No classifiers found")
                return

            else:
                self.classifier_name.clear()
                self.classifier_name.addItems(clf_names)
                self.descriptions.clear()
                for name in clf_names:
                    try:
                        desc = hdf['classifiers/%s' %name].attrs["description"]
                        self.descriptions[name] = desc
                    except KeyError:
                        pass
                self.onClassifierChanged(self.classifier_name.currentText())
            finally:
                hdf.close()

    def loadItems(self, hdf, indices, paths):
        self.progressBar.setMaximum(len(indices))
        self.progressBar.setValue(0)

        self.progressBar.show()

        items = list()
        for i, item in enumerate(hdf.itemsFromClassifier(indices, paths)):
            items.append(item)
            self.progressBar.setValue(i+1)
            QApplication.processEvents()

        self.progressBar.hide()
        self.progressBar.reset()
        return items

    def accept(self):
        if not self._path.text():
            return

        hdf = guessHdfType(self._path.text())
        dmodel = ClfDataModel(self.classifier_name.currentText())
        name = hdf[dmodel.path].attrs[dmodel.NAME]
        lib = hdf[dmodel.path].attrs[dmodel.LIB]

        # switch classifier before loading
        idx = self.parent().classifiers.findText(name)
        if idx < 0:
            QMessageBox.critical(self,
                                 "Error",
                                 "Classifier %s not supported" %name)
            return
        self.parent().classifiers.setCurrentIndex(idx)

        clf = self.parent().currentClassifier()
        model = self.parent().model

        self.parent().removeAll()
        if lib in (dmodel.OneClassSvm, ):
            self._loadSingle(model, hdf, dmodel)
        elif lib in (dmodel.SupportVectorClassifier, ):
            self._loadMultiClass(model, hdf, dmodel)
        else:
            msg = "Classifier %s not supported" %lib
            QMessageBox.critical(self, "Error", msg)

        hdf.close()
        super(LoadAnnotationsDialog, self).accept()

    def _loadMultiClass(self, model, hdf, dmodel):
        norm = hdf[dmodel.normalization].value
        training_data = hdf[dmodel.training_set].value
        classdef = hdf[dmodel.classdef].value
        labels = hdf[dmodel.annotations].value
        sample_info = hdf[dmodel.sample_info].value

        self.parent().removeAll()

        classnames = dict()
        for (name, class_label, color) in classdef:
            classnames[int(class_label)] = name
            model.addClass(name, str(color))

        # keep things sorted for faster loading
        index_array = np.argsort(sample_info["index"])
        classnames = [str(classnames[l]) for l in labels[index_array]]
        idx = sample_info['index'][index_array].tolist()
        paths = sample_info['name'][index_array].tolist()
        items = self.loadItems(hdf, idx, paths)
        for name, item in zip(classnames, items):
            model.addAnnotation(item, name)

        for i in xrange(model.rowCount()):
            model.updateCounts(i)

    def _loadSingle(self, model, hdf, dmodel):
        norm = hdf[dmodel.normalization].value
        training_data = hdf[dmodel.training_set].value
        classdef = hdf[dmodel.classdef].value
        sample_info = hdf[dmodel.sample_info].value

        # keep things sorted for faster loading
        index_array = np.argsort(sample_info["index"])
        idx = sample_info['index'][index_array].tolist()
        paths = sample_info['name'][index_array].tolist()
        items = self.loadItems(hdf, idx, paths)
        for item in items:
            model.addAnnotation(item)

        self.parent().itemCountChanged.emit()
