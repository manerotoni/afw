"""
cellitem.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'LGPL'

__all__ = "CellGraphicsItem"


from PyQt4 import QtGui
from PyQt4 import QtCore

class CellGraphicsItem(QtGui.QGraphicsItemGroup):

    BOUNDARY = 3.0

    def __init__(self, name, *args, **kw):
        super(CellGraphicsItem, self).__init__(*args, **kw)
        self.name = name
        self.setFlag(self.ItemIsSelectable)

    def setImage(self, image):
        self._image = QtGui.QGraphicsPixmapItem()
        self._image.setPixmap(QtGui.QPixmap.fromImage(image))
        self._image.setPos(self.pos())
        self.addToGroup(self._image)

    def paint(self, painter, option, widget):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtCore.Qt.darkGray)

        if self.isSelected():
            rect = self.boundingRect()
            painter.setBrush(QtGui.QColor("#66A3FF"))
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
