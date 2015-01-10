"""
cellitem.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("CellGraphicsItem", "PainterPathItem", "Colors")


import warnings

from PyQt4 import QtGui
from PyQt4 import QtCore

from annot.classifiers.itemclass import UnClassified


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
        self.setAcceptHoverEvents(True)

        self._pixmap = None
        self.class_ = UnClassified
        self.setPixmap(item.pixmap())
        self.features = item.features
        self.frame = item.frame
        self.objid = item.objid
        self.index = item.index
        self.hash = item.hash
        self._is_training_sample = False

        if item.contour is not None:
            for contour, color in item.iterContours():
                self.setContour(contour, color)

        self.setFlag(self.ItemIsSelectable)
        self.sortkey = None

    def __cmp__(self, other):
        return cmp(self.sortkey, other.sortkey)

    def __str__(self):
        return "%s-%s" %(self.frame, self.objid)

    def hoverEnterEvent(self, event):
        txt = ("item: %d\n"
               "class: %s") %(self.index, self.class_.name)
        QtGui.QToolTip.showText(QtGui.QCursor.pos(), txt)

    def _classRect(self):
        rect0 = self.childrenBoundingRect()
        rect = QtCore.QRectF()
        size = self.BOUNDARY*5
        rect.setX(rect0.x())
        rect.setY(rect0.y() + rect0.height() - size)
        rect.setSize(QtCore.QSizeF(size, size))
        return rect

    def _addClassRect(self):
        brush = QtGui.QBrush()
        brush.setStyle(QtCore.Qt.NoBrush)
        brush.setColor(Colors.neutral)
        pen = QtGui.QPen()
        pen.setColor(Colors.neutral)

        pen.setJoinStyle(QtCore.Qt.MiterJoin)

        rect = self._classRect()
        self._classrect = QtGui.QGraphicsRectItem(rect)
        self._classrect.setBrush(brush)
        self._classrect.setPen(pen)
        self._classrect.setZValue(90)
        self._classrect.show()
        self.addToGroup(self._classrect)

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
        self._selrect.setZValue(100)
        self._selrect.hide()
        self.addToGroup(self._selrect)

    def clear(self):
        try:
            self.setClass(UnClassified)
            self.setTrainingSample(False)
        except RuntimeError as e:
            warnings.warn(str(e))


    def setClass(self, class_):
        self.class_ = class_
        if self._is_training_sample:
            self._classrect.setBrush(class_.brush_trainingsample)
        else:
            self._classrect.setBrush(class_.brush)
        self._classrect.setPen(class_.pen)

    def toggleClassIndicator(self, state):

        if state:
            self._classrect.show()
        else:
            # item group does not keep the selection state
            isSelected = self.isSelected()
            self._classrect.hide()
            self.setSelected(isSelected)

    @property
    def pixmap(self):
        return self._pixmap

    def setTrainingSample(self, state):
        assert isinstance(state, bool)
        self._is_training_sample = state

    def isTrainingSample(self):
        return self._is_training_sample

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        item = QtGui.QGraphicsPixmapItem(self)
        item.setPixmap(self.pixmap)
        item.setPos(self.pos())
        self.addToGroup(item)
        self._addSelectorRect()
        self._addClassRect()

    def paint(self, painter, option, widget):
        if self.isSelected():
            self._selrect.show()
        else:
            self._selrect.hide()

    def boundingRect(self):
        rect0 = self.childrenBoundingRect()
        rect = QtCore.QRectF()
        rect.setX(rect0.x())
        rect.setY(rect0.y())
        rect.setSize(rect0.size())
        return rect

    def setPos(self, x, y):
        super(CellGraphicsItem, self).setPos(x, y)

    def setContour(self, contour, color=Colors.neutral):

        pen = QtGui.QPen()
        pen.setColor(color)
        polygon = QtGui.QPolygonF([QtCore.QPointF(*p) for p in contour])
        item = QtGui.QGraphicsPolygonItem(self)
        item.setPolygon(polygon)
        item.setPos(self.pos())
        item.setPen(pen)
        item.setOpacity(0.5)
        self.addToGroup(item)
