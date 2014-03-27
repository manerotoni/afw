"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

__all__ = ("AlfGraphicsView", )

from qimage2ndarray import array2qimage
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import cellh5

from alf.itemgrid import ItemGrid
from alf.cellitem import CellGraphicsItem
from alf.graphicsscene import AlfGraphicsScene


class MouseWheelView(QtGui.QGraphicsView):
    """Graphicsview with zoom and pan feature.

    Mousewheel events scale, Left click and mouse-move drag the the view.
    """

    def __init__(self, *args, **kw):
        super(MouseWheelView, self).__init__(*args, **kw)

        self.setDragMode(self.NoDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorViewCenter)
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(self.SmartViewportUpdate)

    def wheelEvent(self, event):
        if event.delta() > 0:
            factor = 1.1
        else:
            factor = 0.9
        self.scale(factor, factor)

    def mouseReleaseEvent(self, event):

        if event.modifiers() != QtCore.Qt.ControlModifier:
            self.setDragMode(self.NoDrag)
            QtGui.QApplication.restoreOverrideCursor()
        super(MouseWheelView, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):

        if event.modifiers() != QtCore.Qt.ControlModifier:
            self.setDragMode(self.ScrollHandDrag)
            QtGui.QApplication.setOverrideCursor(
                QtGui.QCursor(Qt.ClosedHandCursor))

        super(MouseWheelView, self).mousePressEvent(event)


class AlfGraphicsView(MouseWheelView):

    GSIZE = 50
    NCOLS = 15

    def __init__(self,  file_, region, *args, **kw):
        super(AlfGraphicsView, self).__init__(*args, **kw)

        self.file = file_
        self.region = region
        self._grid = ItemGrid(self.NCOLS, self.GSIZE+4)

        scene = AlfGraphicsScene()
        scene.setBackgroundBrush(QtCore.Qt.darkGray)
        self.setScene(scene)

        self.resize(800, 600)
        self.show()

        for gal in self.iter_gallery(self.file, self.region, self.GSIZE):
            pitem = CellGraphicsItem()
            pitem.setImage(array2qimage(gal))
            pitem.setPos(*self._grid.newPos(pitem))
            scene.addItem(pitem)
            QtGui.QApplication.processEvents()


    def iter_gallery(self, file_, region, size):
        ch5 = cellh5.CH5File(file_, 'r')
        positions = list()
        for k, v in ch5.positions.iteritems():
            positions.extend([(k, v_) for v_ in v])

        pos = ch5.get_position(*positions[0])
        events = pos.get_events().flatten()
        for event in events:
            yield pos.get_gallery_image(event, region, size)
