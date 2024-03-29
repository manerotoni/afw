"""
multiclasssvm.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("Svc", )


import numpy as np
import sklearn.svm

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QSizePolicy

from cat.hdfio.readercore import HdfError
from cat.gui.sidebar.annotation_model import AtMultiClassSvmItemModel
from cat.gui.crossvalidationdlg import CrossValidationDialog
from .classifiers import Classifier, ClfWriter, ClfDataModel


class AnnotationButton(QtWidgets.QToolButton):
    """Custom QToolButton that emits the 'buttonClicked(class_name)' signal.
    The class name is the current text of the name_item."""

    buttonClicked = QtCore.pyqtSignal(str)

    def __init__(self, name_item, *args, **kw):
        super(AnnotationButton, self).__init__(*args, **kw)
        self.setIcon(QtGui.QIcon(":/oxygen/list-add.png"))
        self.setMaximumWidth(self.height())
        self._name_item = name_item

        self.clicked.connect(self.onButtonClicked)

    def onButtonClicked(self):
        self.buttonClicked.emit(self._name_item.text())


class ButtonDelegate(QtWidgets.QItemDelegate):
    """Adds a ToolButton to a ItemView. One needs to open a persitent editor
    if this ItemDelegate is used."""

    def __init__(self, *args, **kw):
        super(ButtonDelegate, self).__init__(*args, **kw)

    def createEditor(self, parent, option, index):

        model = index.model()
        name_item = model.item(index.row(), model.ClassColumn)
        button = AnnotationButton(name_item, parent)
        button.buttonClicked.connect(
            parent.parent().onAnnotationButtonClicked)
        return button

    def setModelData(self, editor, model, index):
        return


class ColorDelegate(QtWidgets.QItemDelegate):
    """Pop up a ColorChooser dialog if the item is going to be edited"""

    def createEditor(self, parent, option, index):
        dlg =  QtWidgets.QColorDialog(parent)
        return dlg

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentColor(QtGui.QColor(index.model().data(index)))
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentColor(), Qt.EditRole)


class TreeView(QtWidgets.QTreeView):

    def __init__(self, annotation_widget, *args, **kw):
        super(TreeView, self).__init__(*args, **kw)
        self._awidget = annotation_widget

        self.setDragDropMode(self.InternalMove)

    def onAnnotationButtonClicked(self, class_name):
        self._awidget.addAnnotation(class_name)


class SvcParameterWidget(QtWidgets.QFrame):

    def __init__(self, parent, *args, **kw):
        super(SvcParameterWidget, self).__init__(parent=parent, *args, **kw)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(2)

        frame = QtWidgets.QToolBar("SVC", self)
        frame.setIconSize(QtCore.QSize(16, 16))

        self.treeview = TreeView(parent, self)
        model = AtMultiClassSvmItemModel(self.treeview)
        model.classesChanged.connect(parent.updateClassifier)
        self.treeview.setModel(model)

        self.treeview.setColumnWidth(0, 75)
        self.treeview.setColumnWidth(1, 75)
        self.treeview.setColumnWidth(2, 30)

        self.addClassBtn = QtWidgets.QToolButton()
        self.addClassBtn.setToolTip("Add new class")
        self.addClassBtn.setIcon(QtGui.QIcon(":/add-class.png"))
        self.addClassBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.addClassBtn.pressed.connect(self.onAddBtn)

        self.removeClassBtn = QtWidgets.QToolButton()
        self.removeClassBtn.setToolTip("Delete selected class")
        self.removeClassBtn.setIcon(QtGui.QIcon(":/remove-class.png"))
        self.removeClassBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.removeClassBtn.pressed.connect(self.onRemoveBtn)
        self.removeClassBtn.pressed.connect(
            parent.predictionInvalid)

        # disable the sanity check whether a sample is already reassign to
        # an other class
        self.allowReassign = QtWidgets.QCheckBox("allow reassign")
        self.allowReassign.stateChanged.connect(model.allowReassign)
        model.allowReassign(self.allowReassign.isChecked())

        self.crossValidBtn = QtWidgets.QToolButton()
        self.crossValidBtn.setToolTip("Cross-validation Dialog")
        self.crossValidBtn.setIcon(QtGui.QIcon(":grid-search.png"))
        self.crossValidBtn.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.crossValidBtn.clicked.connect(parent.validateClassifier)

        frame.addWidget(self.addClassBtn)
        frame.addWidget(self.removeClassBtn)
        frame.addWidget(self.crossValidBtn)
        frame.addWidget(self.allowReassign)

        self.treeview.activated.connect(parent.onActivated)
        self.treeview.setItemDelegateForColumn(1, ColorDelegate(self.treeview))
        self.treeview.setItemDelegateForColumn(2, ButtonDelegate(self.treeview))
        self.treeview.setSelectionMode(self.treeview.ContiguousSelection)

        for row in range(model.rowCount()):
            self.treeview.openPersistentEditor(
                model.index(row, model.ButtonColumn))
        model.layoutChanged.emit()

        vbox.addWidget(frame)
        vbox.addWidget(self.treeview)

        parent.itemCountChanged.connect(self.updateCounts)

    def updateCounts(self):
        for i in xrange(self.treeview.model().rowCount()):
            self.treeview.model().updateCounts(i)

    def onAddBtn(self):
        self.treeview.model().addClass()

    def onRemoveBtn(self):

        model_indices =  self.treeview.selectionModel().selectedRows()
        model_indices.reverse()

        if model_indices:
            ret = QMessageBox.question(
                self, "Confirmation required",
                ("Do you really want to remove the classes"
                 " and all the annotated data?"),
                buttons=QMessageBox.Yes|QMessageBox.No)
        else:
            ret = QMessageBox.No

        if ret == QMessageBox.Yes:

            for mi in model_indices:
                mi2 =  self.treeview.model().parent(mi)
                if not mi2.isValid():
                    self.treeview.model().removeClass(mi)


class SvcWriter(ClfWriter):

    def __init__(self, name, file_, description=None, remove_existing=False):
        super(SvcWriter, self).__init__(file_)
        assert isinstance(remove_existing, bool)

        self.dmodel = ClfDataModel(name)

        if remove_existing:
            try:
                del self.h5f[self.dmodel.path]
            except KeyError:
                pass

        try:
            grp = self.h5f.create_group(self.dmodel.path)
        except ValueError as e:
            raise HdfError("Classifer with name '%s' exists already" %name)

        grp.attrs[self.dmodel.NAME] = Svc.name
        grp.attrs[self.dmodel.LIB] = self.dmodel.SupportVectorClassifier
        grp.attrs[self.dmodel.VERSION] = sklearn.__version__

        if description is not None:
            grp.attrs[self.dmodel.DESCRIPTION] = description

    def saveAnnotations(self, labels):
        # max 256 classes!
        labels = labels.astype(np.uint8)
        dset = self.h5f.create_dataset(self.dmodel.annotations,
                                       data=labels,
                                       compression=self._compression,
                                       compression_opts=self._copts)

    def saveConfusionMatrix(self, confmat):
        dset = self.h5f.create_dataset(self.dmodel.confmatrix,
                                       data=confmat,
                                       compression=self._compression,
                                       compression_opts=self._copts)


class Svc(Classifier):

    KERNEL = "rbf"
    name = "Support Vector Classifier"

    def __init__(self, *args, **kw):
        super(Svc, self).__init__(*args, **kw)
        self._pp = None
        self._cvwidget = None
        self._pwidget = None
        self._clf = sklearn.svm.SVC(C=1.0, kernel=self.KERNEL, gamma=0.0,
                                    probability=True)

    def parameterWidget(self, parent):
        """Returns the classifier specific parameter widget."""
        if self._pwidget is None:
            self._pwidget = SvcParameterWidget(parent)
        return self._pwidget

    def validationDialog(self, parent):
        """Return the classifier specific (cross-)validation widget."""

        if self._cvwidget is None:
            self._cvwidget = CrossValidationDialog(parent, self)
        return self._cvwidget

    def description(self):
        if self._cvwidget is None:
            return ""
        else:
            return self._cvwidget.text()

    def train(self, features, labels):
        self.setupPreProcessor(features)
        self._clf.fit(self._pp(features), labels)

    def predict(self, features):

        if self._clf is None:
            return super(Svc, self).predict(features)
        else:
            features = self._pp(features)
            proba = self._clf.predict_proba(features)

            # turn indices into class labels, asumeing ascending order
            predictions = [self._classes.keys()[i]
                           for i in  np.argmax(proba, axis=1)]

            classes = [self.classes[pred].clone() for pred in predictions]

            for c, p in zip(classes, proba):
                c.score = dict(
                    ((k, v) for k, v in zip(self.classes.keys(), p)))

        return classes

    def saveToHdf(self, name, file_, feature_selection, description,
                  overwrite=False, labels=None, sample_info=None):

        if self._cvwidget is None:
            raise HdfError(("You need to validate the classifier first\n"
                            "Open the Cross validation dialog"))

        writer = SvcWriter(name, file_, description, overwrite)
        writer.saveTrainingSet(self._pp.data, feature_selection.values())
        writer.saveAnnotations(labels)
        writer.saveClassDef(self.classes, self._clf.get_params())
        writer.saveNormalization(self._pp)
        writer.saveConfusionMatrix(self._cvwidget.confusion_matrix)
        writer.saveSampleInfo(sample_info)
        writer.flush()
