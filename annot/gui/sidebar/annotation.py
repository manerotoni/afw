"""
annotation.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtAnnotationWidget", )


from os.path import join, dirname
from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

from annot.hdfio.readercore import HdfError
from annot.classifiers.classifiers import Classifier
from annot.gui.savehdfdlg import SaveClassifierDialog

from .sidebar import NoSampleError
from .sidebar import AtSideBarWidget
from .featuredlg import AtFeatureSelectionDlg
from .annotation_model import DoubleAnnotationError


class AtAnnotationWidget(AtSideBarWidget):


    def __init__(self, *args, **kw):
        super(AtAnnotationWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.featureDlg = AtFeatureSelectionDlg(self)
        self.featureDlg.hide()
        self.saveBtn.clicked.connect(self.onSave)

        self._setupClassifiers()
        self.classifiers.currentIndexChanged.connect(
            self.classifierChanged)

        self.removeBtn.clicked.connect(self.removeSelected)
        self.removeAllBtn.clicked.connect(self.removeAll)
        self.predictBtn.clicked.connect(self.onPredict)
        self.featureBtn.clicked.connect(self.onFeatureBtn)

    def onActivated(self, index):
        parent = self.model.item(index.parent().row(), 0)
        hashkey = parent.child(index.row(), 0).data().toPyObject()
        self.tileview.selectByKey(hashkey)

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

    def predictionInvalid(self, dummy):
        self.setButtonColor(Qt.red)

    def _setupClassifiers(self):

        for name in Classifier.classifiers():
            clf = Classifier(name)
            clf.createActions(self.tileview, self)
            self.classifiers.addItem(name)
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
        for item in items:
            item.setTrainingSample(True)
            self.model.addAnnotation(item, class_name)

    def estimateParameters(self):
        try:
            features = self.filterFeatures(self.model.features)
            clf = self.currentClassifier()
            clf.estimateParameters(features)
        except NoSampleError:
            pass

    def currentClassifier(self):
        return getattr(self, self.classifiers.currentText())

    def itemView(self):
        return self.stack.currentWidget().treeview

    @property
    def model(self):
        return self.itemView().model()

    def setFeatureNames(self, features):
        self.featureDlg.addFeatureList(features)

    def onFeatureBtn(self):
        if self.featureDlg.isHidden():
            self.featureDlg.show()
        else:
            self.featureDlg.hide()

    def onSave(self):

        clf = self.currentClassifier()
        if not self.itemView().model().rowCount():
            QMessageBox.information(self, "information", "Nothing to save!")
            return

        dlg = SaveClassifierDialog(self)
        dlg.name = clf.name

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

        try:
            clf.saveToHdf(dlg.name,
                          hdffile,
                          self.featureDlg.checkedItems(),
                          dlg.description,
                          dlg.overwrite)
        except HdfError as e:
            QMessageBox.critical(self, "error", str(e))
        else:
            QMessageBox.information(self, "information",
                                    "data successfully saved")

    def filterFeatures(self, features):
        """Filter the feature matrix by column wise. Indices of the cols are
        determined by the FeatureSelection Dialog."""

        ftrs_indices = self.featureDlg.indicesOfCheckedItems()

        if not ftrs_indices or features is None:
            raise NoSampleError("no features selected for classifier training")

        return features[:, ftrs_indices]

    def onPredict(self):
        try:
            self.train()
        except NoSampleError:
            pass
        else:
            self.classify(self.tileview.items)
            self.setButtonColor(Qt.darkGreen)

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
