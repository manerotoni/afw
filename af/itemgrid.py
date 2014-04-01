"""
itemgrid.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = 'ItemGrid'

import math
from collections import OrderedDict
from PyQt4 import QtCore


class ItemGrid(QtCore.QObject):

    def __init__(self, cols=10, colwidth=100, *args, **kw):
        super(ItemGrid, self).__init__(*args, **kw)
        self._cols = cols
        self.colwidth = colwidth
        self._positions = OrderedDict()
        self._first_pos = (0, 0)

    def colCount(self):
        return self._cols

    def reorder(self, width):
        self._cols = math.floor(width/self.colwidth)
        old_positions = self._positions
        self._positions = OrderedDict()

        for item in old_positions.keys():
            item.setPos(*self.newPos(item))

    def reset(self):
        self._positions.clear()

    def newPos(self, item):
        nitems = len(self._positions)
        irow = math.ceil(nitems/self._cols)
        icol = nitems % self._cols

        pos =  (icol*self.colwidth, irow*self.colwidth)
        self._positions[item] = pos

        return pos


if __name__ == "__main__":
    ig = ItemGrid(5, 50)
    for i in range(15):
        print ig.newPos(i)
