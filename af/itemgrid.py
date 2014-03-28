"""
itemgrid.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'LGPL'

__all__ = 'ItemGrid'

import math
from PyQt4 import QtCore


class ItemGrid(QtCore.QObject):

    def __init__(self, cols=10, colwidth=100, *args, **kw):
        super(ItemGrid, self).__init__(*args, **kw)
        self._cols = cols
        self._colwidth = colwidth
        self._positions = dict()
        self._first_pos = (0, 0)

    def reset(self):
        self._positions.clear()

    def newPos(self, item):
        nitems = len(self._positions)
        irow = math.ceil(nitems/self._cols)
        icol = nitems % self._cols

        pos =  (icol*self._colwidth, irow*self._colwidth)
        self._positions[item] = pos

        return pos


if __name__ == "__main__":
    ig = ItemGrid(5, 50)
    for i in range(15):
        print ig.newPos(i)
