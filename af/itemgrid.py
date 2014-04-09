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
        self._rect = QtCore.QRectF()
        self._rect.setX(0.0)
        self._rect.setY(0.0)


    def colCount(self):
        return self._cols

    def reorder(self, width):
        self._cols = math.floor(width/self.colwidth)
        for i, item in enumerate(self._positions.keys()):
            irow = math.floor(i/self._cols)
            icol = i % self._cols
            pos =  (icol*self.colwidth, irow*self.colwidth)
            self._positions[item] = pos
            item.setPos(*pos)

        self._rect.setWidth(self._cols*self.colwidth)
        self._rect.setHeight((irow+1)*self.colwidth)

    def rect(self, padding=0.0):

        if padding > 0.0:
            rect = QtCore.QRectF()
            rect.setWidth(self._rect.width()+padding)
            rect.setHeight(self._rect.height()+padding)
            rect.setX(self._rect.x()-padding/2.0)
            rect.setY(self._rect.y()-padding/2.0)
            return rect
        else:
            return self._rect

    def reset(self):
        self._positions.clear()

    def itemCount(self):
        return len(self._positions)

    def newPos(self, item):
        nitems = len(self._positions)
        irow = math.floor(nitems/self._cols)
        icol = nitems % self._cols

        self._rect.setWidth(self._cols*self.colwidth)
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
