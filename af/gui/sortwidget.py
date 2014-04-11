"""
sortwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AfSortWidget')

from os.path import splitext

from PyQt4 import uic
from PyQt4 import QtGui

class AfSortWidget(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(AfSortWidget, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)

    def addRefItems(self, items):
        self.refItems.addItems(items)

    def onClear(self):
        self.refItems.clear()

    def onAdd(self):
        items = self.parent().selectedItems()
        self.addRefItems(items)

    def onSort(self):
        pass
