"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

__all__ = ("AtGraphicsView", )

import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

from cat.itemgrid import ItemGrid
from cat.gui.cellitem import CellGraphicsItem
from cat.gui.graphicsscene import AtGraphicsScene
from cat.gui.toolbars import ViewFlags


class MouseWheelView(QtWidgets.QGraphicsView):
    """Graphicsview with zoom and pan feature.

    Mousewheel events scale, Left click and mouse-move drag the view.
    """

    def __init__(self, *args, **kw):
        super(MouseWheelView, self).__init__(*args, **kw)

        self.setDragMode(self.NoDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.NoAnchor)
        self.setAlignment(QtCore.Qt.AlignJustify)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)

        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(self.SmartViewportUpdate)

    def wheelEvent(self, event):

        if event.modifiers() == QtCore.Qt.ShiftModifier:
            # because apple sucks!
            if (event.angleDelta().y() + event.angleDelta().x()) > 0:
                factor = 1.1
            else:
                factor = 0.9
            self.scale(factor, factor)
        else:
            super(MouseWheelView, self).wheelEvent(event)

    def mouseReleaseEvent(self, event):

        if event.modifiers() != QtCore.Qt.ControlModifier:
            self.setDragMode(self.NoDrag)
            QtWidgets.QApplication.restoreOverrideCursor()
        super(MouseWheelView, self).mouseReleaseEvent(event)

    def mousePressEvent(self, event):

        if event.modifiers() != QtCore.Qt.ControlModifier and \
                event.buttons() == QtCore.Qt.LeftButton:
            self.setDragMode(self.ScrollHandDrag)
            QtWidgets.QApplication.setOverrideCursor(
                QtGui.QCursor(Qt.ClosedHandCursor))

        super(MouseWheelView, self).mousePressEvent(event)


class AtGraphicsView(MouseWheelView):

    itemLoaded = QtCore.pyqtSignal(int)
    emitSelectedItems = QtCore.pyqtSignal(list)

    def __init__(self, parent, gsize, vflags=1, *args, **kw):
        super(AtGraphicsView, self).__init__(parent, *args, **kw)
        self._items = dict()
        self.gsize = gsize
        self._grid = ItemGrid(
            self.gsize+CellGraphicsItem.BoundaryWidth)
        self._hdf = None
        self.vflags = vflags

        scene = AtGraphicsScene()
        scene.setBackgroundBrush(QtCore.Qt.darkGray)
        self.setScene(scene)
        self.createActions()
        self.createContextMenu()

    @property
    def items(self):
        return self._items.values()

    def has_key(self, key):
        return self._items.has_key()

    def hashkeys(self):
        return self._items.keys()

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, item):
        self._items[key] = item

    def setViewFlags(self, vflags):
        self.vflags = vflags

    def zoom(self, factor):
        factor = factor/self.transform().m11()
        self.scale(factor, factor)
        self.reorder(True)

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def createContextMenu(self):
        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.setTearOffEnabled(True)
        self.context_menu.addAction(self.actionRefresh)
        self.context_menu.addAction(self.actionSelectAll)
        self.context_menu.addAction(self.actionInvertSelection)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.actionThrowAnchor)

    def createActions(self):

        self.actionRefresh = QtWidgets.QAction(
            "&Refresh", self, triggered=lambda: self.reorder(True))
        self.actionSelectAll = QtWidgets.QAction("Select &all", self,
                 triggered=self.scene().selectAll)

        self.actionInvertSelection = QtWidgets.QAction(
            "&Invert Selection", self,
            triggered=self.scene().invertSelection)

        self.actionThrowAnchor = QtWidgets.QAction(
            "&Throw Sort Anchor", self,
            triggered=self.parent().onThrowAnchor)

    def toggleClassIndicators(self, state):
        for item in self.items:
            item.toggleClassIndicator(state)

    def toggleMasks(self, state):
        for item in self.items:
            item.toggleMask(state)

    def toggleOutlines(self, state):
        for item in self.items:
            item.toggleOutline(state)

    def toggleDescription(self, state):
        for item in self.items:
            item.toggleDescription(state)

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
        col_count = math.floor(self.size().width()% scaled_colwidth)

        if col_count != self._grid.colCount():
            width = self.size().width()/self.transform().m11()
            self._grid.reorder(width - scaled_colwidth)
            self.scene().setSceneRect(self._grid.rect(5.0))

    def resizeEvent(self, event):
        super(AtGraphicsView, self).resizeEvent(event)
        self.reorder()

    def wheelEvent(self, event):
        super(AtGraphicsView, self).wheelEvent(event)
        self.reorder()

    def clear(self):
        self._abort = True
        self.scene().clear()
        self.scene().setSceneRect(QtCore.QRectF())
        self._grid.reset()
        self._items.clear()

    def addItem(self, items):

        if not isinstance(items, list):
            items = [items]

        for item in items:
            citem = CellGraphicsItem(item)
            citem.setPos(*self._grid.newPos(citem))
            citem.toggleClassIndicator(self.vflags & ViewFlags.Classification)
            citem.toggleOutline(self.vflags & ViewFlags.Outline)
            citem.toggleMask(self.vflags & ViewFlags.Mask)
            citem.toggleDescription(self.vflags & ViewFlags.Description)
            self[citem.hash] = citem
            self.scene().addItem(citem)
            self.scene().setSceneRect(self._grid.rect(5.0))

    def selectByKey(self, hashkey):
        """Set item with hashkey selected and all other items unselected."""
        for item in self.items:
            if item.hash == hashkey:
                item.setSelected(True)
                self.centerOn(item)
            else:
                item.setSelected(False)
