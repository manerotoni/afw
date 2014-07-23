"""
treewidgetitem.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AfTreeWidgetItem", )

from PyQt4 import QtGui
from PyQt4 import QtCore

# for treewidget
class AfTreeWidgetItem(QtGui.QTreeWidgetItem):

    def __init__(self, item, *args, **kw):
        super(AfTreeWidgetItem, self).__init__(*args, **kw)
        self.cellitem = item
        self.setIcon(0, QtGui.QIcon(item.pixmap))
        self.setData(0, QtCore.Qt.DisplayRole, str(item.index))
        self.setData(1, QtCore.Qt.DisplayRole, str(item.frame))
        self.setData(2, QtCore.Qt.DisplayRole, str(item.objid))
