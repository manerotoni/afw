"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfSortWidget', 'AfAnnotationWidget')


from os.path import dirname, join, expanduser

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QFileDialog

from af.sorters import Sorter
from af.classifiers.classifiers import Classifier

from .models import  AfSorterItemModel
from .featuredlg import AtFeatureSelectionDlg


class AfSideBarWidget(QtGui.QWidget):

    def __init__(self, parent, tileview, *args, **kw):
        super(AfSideBarWidget, self).__init__(parent, *args, **kw)
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


class AfSortWidget(AfSideBarWidget):

    startSorting = QtCore.pyqtSignal()

    def __init__(self, *args, **kw):
        super(AfSortWidget, self).__init__(*args, **kw)
        uifile = join(dirname(__file__), self.__class__.__name__ + ".ui")
        uic.loadUi(uifile, self)

        self.treeview.activated.connect(self.onActivated)

        self.sortAlgorithm.addItems(Sorter.sorters())

        self.model = AfSorterItemModel(self)
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



class AfAnnotationWidget(AfSideBarWidget):


    def __init__(self, *args, **kw):
        super(AfAnnotationWidget, self).__init__(*args, **kw)
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

    def _setupClassifiers(self):
        for name in Classifier.classifiers():
            clf = Classifier(name)
            self.classifiers.addItem(name)
            self.stack.addWidget(clf.parameterWidget(self))
            setattr(self, name, clf)

    def estimateParameters(self):
        features = self.filterFeatures(self.model.features)
        clf = self.currentClassifier()
        clf.estimateParameters(features)

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

        try:
            file_ = self.parent.loader.file
            if file_.mode != file_.READWRITE:
                raise IOError("file is read only")
        except (AttributeError, IOError):
            file_ = QFileDialog.getSaveFileName(self, "save Feature Table",
                                                expanduser("~"))

            if not file_:
                return

        ftrnames = self.parent.loader.featureNames
        clf = self.currentClassifier()
        clf.saveToHdf(file_, self.featureDlg.checkedItems())

        QMessageBox.information(self, "information", "data successfully saved")

    def removeAll(self):
        super(AfAnnotationWidget, self).removeAll()
        for item in self.tileview.items:
            item.clearClass()

    def filterFeatures(self, features):
        """Filter the feature matrix by column wise. Indices of the cols are
        determined by the FeatureSelection Dialog."""

        ftrs_indices = self.featureDlg.indicesOfCheckedItems()

        if not(ftrs_indices):
            raise RuntimeError("no features selected for classifier training")

        return features[:, ftrs_indices]

    def removeSelected(self):
        super(AfAnnotationWidget, self).removeSelected()
        self.classify(self.tileview.items)

    def addItems(self, items):
        super(AfAnnotationWidget, self).addItems(items)
        self.train()
        self.classify(self.tileview.items)

    def onPredict(self):
        self.train()
        self.classify(self.tileview.items)

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
