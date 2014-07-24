"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

__all__ = ("AfGraphicsView", )

import math
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from af.itemgrid import ItemGrid
from af.gui.cellitem import CellGraphicsItem
from af.gui.graphicsscene import AfGraphicsScene


class MouseWheelView(QtGui.QGraphicsView):
    """Graphicsview with zoom and pan feature.

    Mousewheel events scale, Left click and mouse-move drag the the view.
    """

    def __init__(self, *args, **kw):
        super(MouseWheelView, self).__init__(*args, **kw)

        self.setDragMode(self.NoDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.NoAnchor)
        self.setAlignment(QtCore.Qt.AlignJustify)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(self.SmartViewportUpdate)

    def wheelEvent(self, event):

        if event.modifiers() == QtCore.Qt.ShiftModifier:
            if event.delta() > 0:
                factor = 1.1
            else:
                factor = 0.9
            self.scale(factor, factor)
        else:
            super(MouseWheelView, self).wheelEvent(event)

    def mouseReleaseEvent(self, event):

        if event.modifiers() != QtCore.Qt.ControlModifier:
            self.setDragMode(self.NoDrag)
            QtGui.QApplication.restoreOverrideCursor()
        super(MouseWheelView, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):

        if event.modifiers() != QtCore.Qt.ControlModifier and \
                event.buttons() == QtCore.Qt.LeftButton:
            self.setDragMode(self.ScrollHandDrag)
            QtGui.QApplication.setOverrideCursor(
                QtGui.QCursor(Qt.ClosedHandCursor))

        super(MouseWheelView, self).mousePressEvent(event)


class AfGraphicsView(MouseWheelView):

    itemLoaded = QtCore.pyqtSignal(int)

    def __init__(self, parent, gsize, *args, **kw):
        super(AfGraphicsView, self).__init__(parent, *args, **kw)
        self.gsize = gsize
        self._grid = ItemGrid(self.gsize+CellGraphicsItem.BOUNDARY)
        self._hdf = None

        scene = AfGraphicsScene()
        scene.setBackgroundBrush(QtCore.Qt.darkGray)
        self.setScene(scene)
        self.createActions()
        self.createContextMenu()

    def zoom(self, factor):
        factor = factor/self.transform().m11()
        self.scale(factor, factor)
        self.reorder(True)

    @property
    def items(self):
        return self._grid.items

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def createContextMenu(self):
        self.context_menu = QtGui.QMenu(self)
        self.context_menu.addAction(self.actionReorder)
        self.context_menu.addAction(self.actionSelectAll)
        self.context_menu.addAction(self.actionAdd)

    def createActions(self):
        self.actionReorder = QtGui.QAction(
            "&refresh", self, triggered=lambda: self.reorder(True))
        self.actionSelectAll = QtGui.QAction("select &all", self,
                                             triggered=self.scene().selectAll)
        self.actionAdd = QtGui.QAction(
            "&add to panel", self, triggered=self.parent().addToToolbox)

    def selectedItems(self):
        return self.scene().selectedItems()

    def updateNColumns(self, width):
        self._grid.ncols = math.floor(
            width/(self.gridSpan()*self.transform().m11())-1)

    def updateRaster(self, gsize):
        self.gsize = gsize
        self._grid.colwidth = self.gsize + self._grid.SPACING

    def gridSpan(self):
        return self.gsize + self._grid.SPACING

    def reorder(self, force_update=False):
        scaled_colwidth = self.transform().m11()*self._grid.colwidth
        col_count = math.floor(self.size().width()%scaled_colwidth)

        if self._grid.colCount() > col_count or force_update:
            width = self.size().width()/self.transform().m11()
            self._grid.reorder(width - scaled_colwidth)
            self.scene().setSceneRect(self._grid.rect(5.0))

    def resizeEvent(self, event):
        super(AfGraphicsView, self).resizeEvent(event)
        self.reorder()

    def wheelEvent(self, event):
        super(AfGraphicsView, self).wheelEvent(event)
        # self.reorder()

    def clear(self):
        self._abort = True
        self.scene().clear()
        self.scene().setSceneRect(QtCore.QRectF())
        self._grid.reset()

    def addItem(self, item):
        citem = CellGraphicsItem(item)
        citem.setPos(*self._grid.newPos(citem))
        self.scene().addItem(citem)
        self.scene().setSceneRect(self._grid.rect(5.0))
