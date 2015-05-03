"""
itemgrid.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = 'ItemGrid'

import math
from PyQt5 import QtCore

class ItemGrid(QtCore.QObject):

    SPACING = 1

    def __init__(self, colwidth=100, ncols=10, *args, **kw):
        super(ItemGrid, self).__init__(*args, **kw)
        self.ncols = ncols
        self.colwidth = colwidth
        self._positions = dict()
        self._rect = QtCore.QRectF()
        self._rect.setX(0.0)
        self._rect.setY(0.0)

    def colCount(self):
        return self.ncols

    @property
    def items(self):
        # unsorted!
        return self._positions.keys()

    def reorder(self, width):
        self.ncols = math.floor(width/self.colwidth)

        skeys = sorted(self.items)

        irow = 0
        for i, item in enumerate(skeys):
            irow = math.floor(i/self.ncols)
            icol = i % self.ncols
            pos =  (icol*self.colwidth, irow*self.colwidth)
            self._positions[item] = pos
            item.setPos(*pos)

        self._rect.setWidth(self.ncols*self.colwidth)
        self._rect.setHeight((irow+1)*self.colwidth)

    def rect(self, padding=0.0):
        rect = QtCore.QRectF()
        rect.setWidth(self._rect.width()+padding)
        rect.setHeight(self._rect.height()+padding+self.colwidth)
        rect.setX(self._rect.x()-padding/2.0)
        rect.setY(self._rect.y()-padding/2.0)
        return rect

    def reset(self):
        self._positions.clear()

    def itemCount(self):
        return len(self._positions)

    def newPos(self, item):
        nitems = len(self._positions)
        item.sortkey = nitems
        irow = math.floor(nitems/self.ncols)
        icol = nitems % self.ncols

        self._rect.setWidth(self.ncols*self.colwidth)
        self._rect.setHeight(irow*self.colwidth )

        if self._positions.has_key(item):
            raise RuntimeError("cannot add the same item twice")

        pos =  (icol*self.colwidth, irow*self.colwidth)
        self._positions[item] = pos

        return pos


if __name__ == "__main__":
    ig = ItemGrid(5, 50)
    for i in range(15):
        print ig.newPos(i)
