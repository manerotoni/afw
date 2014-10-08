"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtSortWidget', 'AtAnnotationWidget')


from os.path import dirname, join

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox

from annot.sorters import Sorter
from annot.hdfio.readercore import HdfError
from annot.classifiers.classifiers import Classifier
from annot.gui.savehdfdlg import SaveClassifierDialog

from .models import  AtSorterItemModel
from .featuredlg import AtFeatureSelectionDlg


class NoSampleError(Exception):
    pass


class AtSideBarWidget(QtGui.QWidget):

    def __init__(self, parent, tileview, *args, **kw):
        super(AtSideBarWidget, self).__init__(parent, *args, **kw)
        self.tileview = tileview
        self.parent = parent

    def removeSelected(self):
        model_indices =  self.treeview.selectionModel().selectedRows()
        model_indices.reverse()

        for mi in model_indices:
            self.model.removeRow(mi.row())

    def removeAll(self):
        self.model.clear()

    def addItems(self, items):
        for item in items:
            self.model.addItem(item)

    def onAdd(self):
        items = self.tileview.selectedItems()
        self.addItems(items)

    def onActivated(self, index):
        item = self.model.item(index.row())
        self.tileview.selectByIndex(int(item.text()))


class AtSortWidget(AtSideBarWidget):

    startSorting = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AtSortWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.treeview.activated.connect(self.onActivated)

        self.sortAlgorithm.addItems(Sorter.sorters())

        self.model = AtSorterItemModel(self)
        self.treeview.setModel(self.model)

        self.removeBtn.clicked.connect(self.removeSelected)
        self.removeAllBtn.clicked.connect(self.removeAll)
        self.addBtn.clicked.connect(self.onAdd)
        self.sortBtn.clicked.connect(self.sort)
        self.startSorting.connect(
            lambda: self.tileview.reorder(force_update=True))

    def sort(self):

        all_items = self.tileview.items

        # nothing to sort
        if not all_items:
            return

        sorter = Sorter(self.sortAlgorithm.currentText(), all_items)
        sorter.treedata = self.model.features

        try:
            dist = sorter()
        except Exception as e:
            QMessageBox.warning(self, 'Warning', str(e))
            return

        if dist is not None:
            for d, item in zip(dist, all_items):
                item.sortkey = d
            self.startSorting.emit()


class AtAnnotationWidget(AtSideBarWidget):


    def __init__(self, *args, **kw):
        super(AtAnnotationWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)
        self.treeview.activated.connect(self.onActivated)
        self.featureDlg = AtFeatureSelectionDlg(self)
        self.featureDlg.hide()

        self.stack = QtGui.QStackedWidget(self)
        self.stack.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Maximum)
            )

        self.sbox.addWidget(self.stack)
        self.saveBtn.clicked.connect(self.onSave)

        self._setupClassifiers()
        self.classifiers.currentIndexChanged.connect(
            self.stack.setCurrentIndex)

        self.treeview.setModel(self.model)

        self.removeBtn.clicked.connect(self.removeSelected)
        self.removeAllBtn.clicked.connect(self.removeAll)
        self.predictBtn.clicked.connect(self.onPredict)
        self.addBtn.clicked.connect(self.onAdd)
        self.featureBtn.clicked.connect(self.onFeatureBtn)

    def setButtonColor(self, color):
        color = QtGui.QColor(color).name()
        qss = "QPushButton#predictBtn {color: %s}" %color
        self.predictBtn.setStyleSheet(qss)

    def predictionInvalid(self, dummy):
        self.setButtonColor(Qt.red)

    def _setupClassifiers(self):

        # import pdb; pdb.set_trace()

        for name in Classifier.classifiers():
            clf = Classifier(name)
            clf.createActions(self.tileview, self)
            print clf.actions
            self.classifiers.addItem(name)
            self.stack.addWidget(clf.parameterWidget(self))
            setattr(self, name, clf)

        clf = self.currentClassifier()
        self.setAnnotationActions(clf.actions)

    def setAnnotationActions(self, actions):
        self.tileview.clearActions()
        self.tileview.addActions(actions)

    def addAnnotation(self, class_name):
        self.addItems(self.tileview.selectedItems(), class_name)

    def estimateParameters(self):
        try:
            features = self.filterFeatures(self.model.features)
            clf = self.currentClassifier()
            clf.estimateParameters(features)
        except NoSampleError:
            pass

    def currentClassifier(self):
        return getattr(self, self.classifiers.currentText())

    @property
    def model(self):
        return self.currentClassifier().model

    def setFeatureNames(self, features):
        self.featureDlg.addFeatureList(features)

    def onFeatureBtn(self):
        if self.featureDlg.isHidden():
            self.featureDlg.show()
        else:
            self.featureDlg.hide()

    def onSave(self):

        clf = self.currentClassifier()
        if not clf.model.rowCount():
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

    def removeSelected(self):
        self.setButtonColor(Qt.red)
        super(AtAnnotationWidget, self).removeSelected()


    def addItems(self, items, class_name):

        self.setButtonColor(Qt.red)
        for item in items:
            item.setTrainingSample(True)
            self.model.addItem(item)

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
        clf.train(features)

    def classify(self, items):
        clf = self.currentClassifier()
        for item in items:
            features = self.filterFeatures(item.features.reshape((1, -1)))
            prediction = clf.predict(features)
            item.setClass(prediction[0])
