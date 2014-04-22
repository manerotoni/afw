"""
cellitem.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("CellGraphicsItem", "PainterPathItem", "Colors")


from qimage2ndarray import array2qimage

from PyQt4 import QtGui
from PyQt4 import QtCore


class Colors(object):
    # selected = QtGui.QColor("#87CEFA")
    selected = QtGui.QColor("blue")
    neutral = QtGui.QColor("white")


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

    BOUNDARY = 2.0

    def __init__(self, item, *args, **kw):
        super(CellGraphicsItem, self).__init__(*args, **kw)

        self.setImage(array2qimage(item.image))

        self.features = item.features
        self.frame = item.frame
        self.objid = item.objid

        if item.contour is not None:
            self.setContour(item.contour)

        self.setFlag(self.ItemIsSelectable)
        self.sortkey = None

    def __cmp__(self, other):
        return cmp(self.sortkey, other.sortkey)

    def __str__(self):
        return "%s-%s" %(self.frame, self.objid)

    def _selectorRect(self):
        rect0 = self.childrenBoundingRect()
        rect = QtCore.QRectF()
        rect.setX(rect0.x() + self.BOUNDARY/2)
        rect.setY(rect0.y() + self.BOUNDARY/2)
        rect.setSize(
            rect0.size() - QtCore.QSizeF(self.BOUNDARY, self.BOUNDARY))
        return rect

    def _addSelectorRect(self):
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.NoBrush)
        pen = QtGui.QPen()
        pen.setColor(Colors.selected)
        pen.setWidthF(self.BOUNDARY)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)

        rect = self._selectorRect()
        self._selrect = QtGui.QGraphicsRectItem(rect)
        self._selrect.setBrush(brush)
        self._selrect.setPen(pen)
        self._selrect.hide()
        self.addToGroup(self._selrect)

    @property
    def pixmap(self):
        return self._pixmap

    def setImage(self, image):
        self._pixmap = QtGui.QPixmap.fromImage(image)
        item = QtGui.QGraphicsPixmapItem(self)
        item.setPixmap(self.pixmap)
        item.setPos(self.pos())
        self.addToGroup(item)
        self._addSelectorRect()

    def paint(self, painter, option, widget):
        if self.isSelected():
            self._selrect.show()
        else:
            self._selrect.hide()

            # rect = self.boundingRect()
            # painter.setBrush(Colors.selected)
            # painter.drawRect(rect)

    def boundingRect(self):
        rect0 = self.childrenBoundingRect()
        rect = QtCore.QRectF()
        rect.setX(rect0.x())
        rect.setY(rect0.y())
        rect.setSize(rect0.size())
        return rect

    def setPos(self, x, y):
        super(CellGraphicsItem, self).setPos(x, y)

    def setContour(self, contour):

        pen = QtGui.QPen()
        pen.setColor(Colors.neutral)
        polygon = QtGui.QPolygonF([QtCore.QPointF(*p) for p in contour])
        item = QtGui.QGraphicsPolygonItem(self)
        item.setPolygon(polygon)
        item.setPos(self.pos())
        item.setPen(pen)
        item.setOpacity(0.5)
        self.addToGroup(item)
