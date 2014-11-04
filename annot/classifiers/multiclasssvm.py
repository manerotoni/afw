"""
multiclasssvm.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("MultiClassSvm", )


import sklearn.svm
from PyQt4 import QtGui
from PyQt4.QtGui import QMessageBox
from PyQt4 import QtCore
from PyQt4.QtCore import Qt


from annot.gui.sidebar.annotation_model import AtMultiClassSvmItemModel
from annot.gui.crossvalidationdlg import CrossValidationDialog
from .classifiers import Classifier


class AnnotationButton(QtGui.QToolButton):
    """Custom QToolButton that emits the 'buttonClicked(class_name)' signal.
    The class name is the current text of the name_item."""


    buttonClicked = QtCore.pyqtSignal(str)

    def __init__(self, name_item, *args, **kw):
        super(AnnotationButton, self).__init__(*args, **kw)
        self.setText('+')
        self.setMaximumWidth(self.height())
        self._name_item = name_item

        self.clicked.connect(self.onButtonClicked)

    def onButtonClicked(self):
        self.buttonClicked.emit(self._name_item.text())


class ButtonDelegate(QtGui.QItemDelegate):
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


class ColorDelegate(QtGui.QItemDelegate):
    """Pop up a ColorChooser dialog if the item is going to be edited"""

    def createEditor(self, parent, option, index):
        dlg =  QtGui.QColorDialog(parent)
        return dlg

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentColor(QtGui.QColor(index.model().data(index)))
        editor.blockSignals(False)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.currentColor(), Qt.EditRole)


class TreeView(QtGui.QTreeView):

    def __init__(self, annotation_widget, *args, **kw):
        super(TreeView, self).__init__(*args, **kw)
        self._awidget = annotation_widget

    def onAnnotationButtonClicked(self, class_name):
        self._awidget.addAnnotation(class_name)


class McSvmParameterWidget(QtGui.QFrame):

    def __init__(self, parent, *args, **kw):
        super(McSvmParameterWidget, self).__init__(parent=parent, *args, **kw)

        gbox = QtGui.QGridLayout(self)
        gbox.setContentsMargins(2, 2, 2, 2)
        gbox.setSpacing(2)

        self.treeview = TreeView(parent, self)
        model = AtMultiClassSvmItemModel(self.treeview)
        model.classesChanged.connect(parent.updateClassifier)
        self.treeview.setModel(model)

        self.addClassBtn = QtGui.QPushButton("new class")
        self.addClassBtn.pressed.connect(self.onAddBtn)

        self.removeClassBtn = QtGui.QPushButton("remove class")
        self.removeClassBtn.pressed.connect(self.onRemoveBtn)

        # disable the sanity check whether a sample is already reassign to
        # an other class
        self.allowReassign = QtGui.QCheckBox("allow reassign")
        self.allowReassign.stateChanged.connect(model.allowReassign)
        model.allowReassign(self.allowReassign.isChecked())

        self.crossValidBtn = QtGui.QPushButton("cross validation")
        self.crossValidBtn.clicked.connect(parent.validateClassifier)


        gbox.addWidget(self.addClassBtn, 0, 0)
        gbox.addWidget(self.removeClassBtn, 0, 1)
        gbox.addWidget(self.crossValidBtn, 2, 0)
        gbox.addWidget(self.allowReassign, 2, 1)

        self.treeview.activated.connect(parent.onActivated)
        self.treeview.setItemDelegateForColumn(1, ColorDelegate(self.treeview))
        self.treeview.setItemDelegateForColumn(2, ButtonDelegate(self.treeview))
        self.treeview.setSelectionMode(self.treeview.ContiguousSelection)

        for row in range(model.rowCount()):
            self.treeview.openPersistentEditor(
                model.index(row, model.ButtonColumn))
        model.layoutChanged.emit()

        gbox.addWidget(self.treeview, 3, 0, 1, 0)

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


class MultiClassSvm(Classifier):

    KERNEL = "rbf"
    name = "svc"

    def __init__(self, *args, **kw):
        super(MultiClassSvm, self).__init__(*args, **kw)
        self._pp = None
        self._cvwidget = None
        self._pwidget = None
        self._clf = sklearn.svm.SVC(C=1.0, kernel=self.KERNEL, gamma=0.0)

    def setParameters(self, params):
        assert isinstance(params, dict)
        self._clf.set_params(**params)

    def parameterWidget(self, parent):
        """Returns the classifier specific parameter widget."""
        if self._pwidget is None:
            self._pwidget = McSvmParameterWidget(parent)
        return self._pwidget

    def validationDialog(self, parent):
        """Return the classifier specific (cross-)validation widget."""

        if self._cvwidget is None:
            self._cvwidget = CrossValidationDialog(parent, self)
        return self._cvwidget

    def saveToHdf(self, *args, **kw):
        pass

    def train(self, features, labels):
        self.setupPreProcessor(features)
        self._clf.fit(self._pp(features), labels)

    def predict(self, features):

        if self._clf is None:
            return super(MultiClassSvm, self).predict(features)
        else:
            predictions = self._clf.predict(self._pp(features))
            return [self.classes[pred] for pred in predictions]
