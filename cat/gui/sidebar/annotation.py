"""
annotation.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtAnnotationWidget", )


import warnings

from os.path import join, dirname

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMessageBox

from cat.classifiers.classifiers import Classifier
from cat.gui.loadui import loadUI
from cat.gui.saveclassifierdlg import SaveClassifierDialog
from cat.gui.loadclassifierdlg import LoadClassifierDialog

from .sidebar import NoSampleError
from .sidebar import AtSideBarWidget
from .annotation_model import DoubleAnnotationError


class AtAnnotationWidget(AtSideBarWidget):


    def __init__(self, *args, **kw):
        super(AtAnnotationWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        loadUI(uifile, self)

        self._classifier_is_valid = False

        self.saveBtn.clicked.connect(self.onSave)
        self.loadBtn.clicked.connect(self.onLoadAnnotations)

        self._setupClassifiers()
        self.classifiers.currentIndexChanged.connect(
            self.classifierChanged)

        self.removeBtn.clicked.connect(self.removeSelected)
        self.removeAllBtn.clicked.connect(self.removeAll)
        self.predictBtn.clicked.connect(self.onPredict)
        self.predictBtn.setText('Predict')

        self.tileview.emitSelectedItems.connect(
            self.selectByHashes)

    def removeAll(self):
        super(AtAnnotationWidget, self).removeAll()
        self.setButtonColor(Qt.red)
        self.clearItems()

    def removeSelected(self):
        super(AtAnnotationWidget, self).removeSelected()
        self.setButtonColor(Qt.red)

    def onActivated(self, index):
        hkey = self.model.hashkey(index)
        self.tileview.selectByKey(hkey)

    def classifierChanged(self, index):
        self.stack.setCurrentIndex(index)
        clf = self.currentClassifier()

    def updateClassifier(self, classes):
        # XXX workaround slot. Parent of a classifier uses the Factory metaclass
        # and is not a QObject --> it segfaults if it is a QObject
        clf = self.currentClassifier()
        clf.setClasses(classes, self.tileview, self)

    def setCurrentClassifier(self, name):
        index = self.classifiers.findText(name)
        if index >= 0:
            self.classifiers.setCurrentIndex(index)

    def setButtonColor(self, color):
        if color == Qt.red:
            self._classifier_is_valid = False

        color = QtGui.QColor(color).name()
        qss = "QPushButton#predictBtn {color: %s}" %color
        self.predictBtn.setStyleSheet(qss)

    def predictionInvalid(self, dummy=None):
        self.setButtonColor(Qt.red)

    def _setupClassifiers(self):

        for name in Classifier.classifiers():
            clf = Classifier(name)
            self.classifiers.addItem(clf.name, userData=name)
            self.stack.addWidget(clf.parameterWidget(self))
            setattr(self, name, clf)

        clf = self.currentClassifier()

    def setAnnotationActions(self, actions):
        self.tileview.clearActions()
        self.tileview.addActions(actions)

    def addAnnotation(self, class_name):
        try:
            self.addItems(self.tileview.selectedItems(), class_name)
            self.clearSelection()
        except DoubleAnnotationError as e:
            QMessageBox.warning(self, "Warning", str(e))

    def addItems(self, items, class_name):
        self.setButtonColor(Qt.red)
        clf = self.currentClassifier()
        class_ = clf.classByName(class_name)
        for item in items:
            item.setTrainingSample(class_)
            self.model.addAnnotation(item, class_name)
        self.itemCountChanged.emit()

    def estimateParameters(self):
        try:
            features = self.filterFeatures(self.model.features)
            clf = self.currentClassifier()
            clf.estimateParameters(features)
            self.predictionInvalid()
        except NoSampleError:
            pass

    def validateClassifier(self):
        try:
            vd = self.currentClassifier().validationDialog(self)
            vd.show()
            vd.raise_()
            self._classifier_is_valid = True
        except NoSampleError:
            return

    def currentClassifier(self):
        index = self.classifiers.currentIndex()
        name = self.classifiers.itemData(index)
        return getattr(self, name)

    def setClassifierParameters(self, params):
        clf = self.currentClassifier()
        clf.setParameters(params)

    def itemView(self):
        return self.stack.currentWidget().treeview

    @property
    def model(self):
        return self.itemView().model()

    def setFeatureNames(self, features):
        self.featuredlg.addFeatureList(features)

    def onPredict(self):

        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.train()

            if not self._classifier_is_valid:
                qmb = QMessageBox(QMessageBox.Question,
                                  "Grid search & Cross Validation",
                                  ("You need to run Grid Search & "
                                   " Cross Validation before you predict"),
                                  parent=self)
                ignoreBtn = qmb.addButton(qmb.Ignore)
                cancelBtn = qmb.addButton(qmb.Cancel)
                runBtn = qmb.addButton(
                    "Run Grid Search", qmb.AcceptRole)
                qmb.exec_()

                if qmb.clickedButton() == runBtn:
                    self.validateClassifier()
                elif qmb.clickedButton() == ignoreBtn:
                    pass
                elif qmb.clickedButton() == cancelBtn:
                    return

        except NoSampleError:
            pass
        else:
            self.classify(self.tileview.items)
            self.setButtonColor(Qt.darkGreen)
        finally:
            QApplication.restoreOverrideCursor()

    def train(self):
        features = self.filterFeatures(self.model.features)
        clf = self.currentClassifier()
        clf.train(features, self.model.labels)

    def classify(self, items):
        clf = self.currentClassifier()
        for item in items:
            features = self.filterFeatures(item.features.reshape((1, -1)))
            try:
                prediction = clf.predict(features)
                item.setClass(prediction[0])
            except ValueError:
                warnings.warn("feature vector contains NaN's")

    def onSave(self):
        clf = self.currentClassifier()
        if not self.itemView().model().rowCount():
            return

        labels = self.itemView().model().labels
        sinfo = self.itemView().model().sample_info

        dlg = SaveClassifierDialog(clf, labels, sinfo, parent=self,
                                   description=clf.description())
        dlg.path = self.parent.loader.file.filename
        dlg.exec_()

    def clearItems(self):
        for item in self.tileview.items:
            item.clear()

    def onLoadAnnotations(self):

        try:
            file_ = self.parent.loader.file.filename
        except AttributeError:
            return
        dlg = LoadClassifierDialog(file_, self)

        if dlg.result() != dlg.Rejected:
            dlg.exec_()

        if dlg.result() == dlg.Accepted:
            self.setButtonColor(Qt.red)
            # in this case the classifier is valid but
            self._classifier_is_valid = True
