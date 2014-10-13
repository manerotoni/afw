"""
annotation_model.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ =("AtMultiClassSvmItemModel", )


from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from .models import AtStandardItemModel


class AtMultiClassSvmItemModel(AtStandardItemModel):

    ClassColumn = 0
    ColorColumn = 1
    ButtonColumn = 2

    def __init__(self, *args, **kw):
        super(AtMultiClassSvmItemModel, self).__init__(*args, **kw)

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

    def removeClass(self, modelindex):
        self.removeRow(modelindex.row())

    def prepareRowItems(self, item):
        """Prepare annotation items which are added as childs to
        to a top level item a.k.a. class item"""

        items = [QtGui.QStandardItem(QtGui.QIcon(item.pixmap), str(item.index)),
                 QtGui.QStandardItem(str(item.frame)),
                 QtGui.QStandardItem(str(item.objid))]
        for item in items:
            item.setEditable(False)
        return items

    def addAnnotation(self, item, class_name):
        item = self.findClassItems(class_name)[0]
        childs = self.prepareRowItems(item)
        item.appendRow(childs)
