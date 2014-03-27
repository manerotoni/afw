"""
cellitem.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'LGPL'

__all__ = ("CellGraphicsItem", "PainterPathItem", "Colors")


from PyQt4 import QtGui
from PyQt4 import QtCore

class Colors(object):
    selected = QtGui.QColor("#87CEFA")


class PainterPathItem(QtGui.QGraphicsPathItem):
    # custom PainterPathItem fixes path() method. Did not return the same
    # instance, that was used when the item was created

    def __init__(self, path, *args, **kw):
        super(PainterPathItem, self).__init__(path, *args, **kw)
        self._path = path

    def path(self):
        return self._path


class CellGraphicsItem(QtGui.QGraphicsItemGroup):
    """Item group to show a pixmap, the segmentation and annotation as one item.
    """

    BOUNDARY = 4.0

    def __init__(self, *args, **kw):
        super(CellGraphicsItem, self).__init__(*args, **kw)
        self.setFlag(self.ItemIsSelectable)

    def setImage(self, image):
        item = QtGui.QGraphicsPixmapItem()
        item.setPixmap(QtGui.QPixmap.fromImage(image))
        item.setPos(self.pos())
        self.addToGroup(item)

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.darkGray)

        if self.isSelected():
            rect = self.boundingRect()
            painter.setBrush(Colors.selected)
            painter.drawRect(rect)

    def boundingRect(self):
        rect0 = self.childrenBoundingRect()
        rect = QtCore.QRectF()
        rect.setX(rect0.x() - self.BOUNDARY/2)
        rect.setY(rect0.y() - self.BOUNDARY/2)
        rect.setSize(
            rect0.size() + QtCore.QSizeF(self.BOUNDARY, self.BOUNDARY))
        return rect

    def setPos(self, x, y):
        super(CellGraphicsItem, self).setPos(x, y)

    def setContour(self, contour):
        pass
