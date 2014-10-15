"""
multiclasssvm.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("MultiClassSvm", )


from PyQt4 import QtGui
from PyQt4.QtGui import QMessageBox
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

from annot.gui.sidebar.annotation_model import AtMultiClassSvmItemModel
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

        self.treeview = TreeView(parent, self)
        model = AtMultiClassSvmItemModel(self.treeview)
        model.classesChanged.connect(parent.updateClassifier)
        self.treeview.setModel(model)

        self.addClassBtn = QtGui.QPushButton("add class")
        self.addClassBtn.pressed.connect(self.onAddBtn)

        self.removeClassBtn = QtGui.QPushButton("remove class")
        self.removeClassBtn.pressed.connect(self.onRemoveBtn)

        gbox.addWidget(self.addClassBtn, 0, 0)
        gbox.addWidget(self.removeClassBtn, 0, 1)

        self.treeview.activated.connect(parent.onActivated)
        self.treeview.setItemDelegateForColumn(1, ColorDelegate(self.treeview))
        self.treeview.setItemDelegateForColumn(2, ButtonDelegate(self.treeview))
        self.treeview.setSelectionMode(self.treeview.ContiguousSelection)

        for row in range(model.rowCount()):
            self.treeview.openPersistentEditor(
                model.index(row, model.ButtonColumn))
        model.layoutChanged.emit()

        gbox.addWidget(self.treeview, 1, 0, 1, 0)

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

    def __init__(self, *args, **kw):
        super(MultiClassSvm, self).__init__(*args, **kw)
        self._pp = None

    def parameterWidget(self, parent):
        self._params = McSvmParameterWidget(parent)
        return self._params

    def saveToHdf(self, *args, **kw):
        pass

    def train(self, *args, **kw):
        pass

    def predict(self, *args, **kw):
        pass
