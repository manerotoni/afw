"""
annotation.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtAnnotationWidget", )


from os.path import join, dirname
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QApplication, QCursor, QMessageBox

from cat.hdfio.readercore import HdfError
from cat.classifiers.classifiers import Classifier
from cat.gui.savehdfdlg import SaveClassifierDialog

from .sidebar import NoSampleError
from .sidebar import AtSideBarWidget
from .annotation_model import DoubleAnnotationError


class AtAnnotationWidget(AtSideBarWidget):


    def __init__(self, *args, **kw):
        super(AtAnnotationWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.saveBtn.clicked.connect(self.onSave)

        self._setupClassifiers()
        self.classifiers.currentIndexChanged.connect(
            self.classifierChanged)

        self.removeBtn.clicked.connect(self.removeSelected)
        self.removeAllBtn.clicked.connect(self.removeAll)
        self.predictBtn.clicked.connect(self.onPredict)
        self.predictBtn.setText('Predict')

    def onActivated(self, index):
        self.tileview.selectByKey(self.model.hashkey(index))

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
        color = QtGui.QColor(color).name()
        qss = "QPushButton#predictBtn {color: %s}" %color
        self.predictBtn.setStyleSheet(qss)

    def predictionInvalid(self, dummy=None):
        self.setButtonColor(Qt.red)

    def _setupClassifiers(self):

        for name in Classifier.classifiers():
            clf = Classifier(name)
            clf.createActions(self.tileview, self)
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
        except DoubleAnnotationError as e:
            QMessageBox.warning(self, "Warning", str(e))

    def addItems(self, items, class_name):
        self.setButtonColor(Qt.red)
        clf = self.currentClassifier()
        class_ = clf.classByName(class_name)
        for item in items:
            item.setTrainingSample(class_)
            self.model.addAnnotation(item, class_name)

    def estimateParameters(self):
        try:
            features = self.filterFeatures(self.model.features)
            clf = self.currentClassifier()
            clf.estimateParameters(features)
            self.predictionInvalid()
        except NoSampleError:
            pass

    def validateClassifier(self):
        vd = self.currentClassifier().validationDialog(self)
        vd.show()
        vd.raise_()

    def currentClassifier(self):
        index = self.classifiers.currentIndex()
        name = self.classifiers.itemData(index).toPyObject()
        return getattr(self, name)

    def itemView(self):
        return self.stack.currentWidget().treeview

    @property
    def model(self):
        return self.itemView().model()

    def setFeatureNames(self, features):
        self.featuredlg.addFeatureList(features)

    def onSave(self):
        clf = self.currentClassifier()
        if not self.itemView().model().rowCount():
            QMessageBox.information(self, "information", "Nothing to save!")
            return

        dlg = SaveClassifierDialog(self)
        dlg.name = clf.name.replace(" ", "_").lower()

        hdffile = self.parent.loader.file
        if hdffile is None or hdffile.mode != hdffile.READWRITE:
            dlg.path = ""
        else:
            dlg.path = hdffile.filename

        dlg.exec_()

        if dlg.result() == dlg.Rejected:
            return

        if hdffile.filename != dlg.path:
            hdffile = dlg.path

        labels = self.itemView().model().labels
        sinfo = self.itemView().model().sample_info
        try:
            clf.saveToHdf(dlg.name,
                          hdffile,
                          self.featuredlg.checkedItems(),
                          dlg.description,
                          dlg.overwrite,
                          labels,
                          sinfo)
        except HdfError as e:
            QMessageBox.critical(self, "error", str(e))
        else:
            QMessageBox.information(self, "information",
                                    "Data saved successfully")

    def onPredict(self):

        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.train()
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
            prediction = clf.predict(features)
            item.setClass(prediction[0])
