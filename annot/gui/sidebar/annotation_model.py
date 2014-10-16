"""
annotation_model.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ =("AtMultiClassSvmItemModel", )


from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

from annot.classifiers.itemclass import ItemClass
from .models import AtStandardItemModel


class AtMultiClassSvmItemModel(AtStandardItemModel):

    ClassColumn = 0
    ColorColumn = 1
    ButtonColumn = 2

    classesChanged = QtCore.pyqtSignal(dict)

    def __init__(self, *args, **kw):
        super(AtMultiClassSvmItemModel, self).__init__(*args, **kw)

        # only top level items are editable
        self.dataChanged.connect(self.onDataChanged)

    def _setHeader(self):
        # default columns
        self.setHeaderData(0, Qt.Horizontal, "class")
        self.setHeaderData(1, Qt.Horizontal, "color")
        self.setHeaderData(2, Qt.Horizontal, "button")

    def _brushFromColor(self, color):
        color = QtGui.QColor(color)
        brush = QtGui.QBrush()
        brush.setColor(color)
        brush.setStyle(Qt.SolidPattern)
        return brush

    def setData(self, index, value, role):

        if index.column() == self.ColorColumn:
            self.item(index.row(), index.column()).setBackground(
                self._brushFromColor(value))

        return super(AtMultiClassSvmItemModel, self).setData(index, value, role)

    def findClassItems(self, class_name, match=Qt.MatchExactly):

        items = super(AtMultiClassSvmItemModel, self).findItems(
            class_name, match, self.ClassColumn)

        if not items:
            raise RuntimeError("No Item with content '%s' found" %class_name)
        else:
            return items[0]

    def onDataChanged(self, topleft, bottomright):
        self.emitClassesChanged()

    def currentClasses(self):
        """Construct a class defintion from the model by iteration over
        the 'toplevel items'."""

        classes = dict()
        for i in range(self.rowCount()):
            class_item = self.item(i, self.ClassColumn)
            color_item = self.item(i, self.ColorColumn)

            name = class_item.text()
            color = color_item.text()
            classes[i] = ItemClass(name, QtGui.QColor(color), i)

        return classes

    def emitClassesChanged(self):
        """Read the class defintion and emit the 'classesChanged' signal.
        This method must be called whenever a class is add or remove or the
        name or color of a class has changed."""

        classes = self.currentClasses()
        self.classesChanged.emit(classes)

    def addClass(self, name='unnamed', color='#e3e3e3'):

        items = self.findItems(name, Qt.MatchStartsWith, self.ClassColumn)
        if items:
            name = ''.join([name, str(len(items))])
        elif name == "unnamed":
            name = "unnamed0"

        name_item = QtGui.QStandardItem(name)
        color_item = QtGui.QStandardItem(color)
        color_item.setBackground(self._brushFromColor(color))
        button_item = QtGui.QStandardItem()

        name_item.setEditable(True)
        color_item.setEditable(True)
        self.appendRow([name_item, color_item, button_item])

        self.parent().openPersistentEditor(
            self.index(self.rowCount()-1, self.ButtonColumn))

        self.layoutChanged.emit()
        self.emitClassesChanged()

    def removeClass(self, modelindex):
        self.removeRow(modelindex.row())
        self.emitClassesChanged()

    def addAnnotation(self, item, class_name):
        class_item = self.findClassItems(class_name)
        childs = self.prepareRowItems(item)
        class_item.appendRow(childs)
