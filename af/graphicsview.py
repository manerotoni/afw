"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

__all__ = ("AfGraphicsView", )

import math
import numpy as np
from qimage2ndarray import array2qimage
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from af.itemgrid import ItemGrid
from af.cellitem import CellGraphicsItem
from af.graphicsscene import AfGraphicsScene
from af.hdfio import HdfReader, HdfCoord


class MouseWheelView(QtGui.QGraphicsView):
    """Graphicsview with zoom and pan feature.

    Mousewheel events scale, Left click and mouse-move drag the the view.
    """

    def __init__(self, *args, **kw):
        super(MouseWheelView, self).__init__(*args, **kw)

        self.setDragMode(self.NoDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.NoAnchor)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

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

        if event.modifiers() != QtCore.Qt.ControlModifier:
            self.setDragMode(self.ScrollHandDrag)
            QtGui.QApplication.setOverrideCursor(
                QtGui.QCursor(Qt.ClosedHandCursor))

        super(MouseWheelView, self).mousePressEvent(event)


class AfGraphicsView(MouseWheelView):

    NCOLS = 15
    itemLoaded = QtCore.pyqtSignal(int)

    def __init__(self, parent, gsize, *args, **kw):
        super(AfGraphicsView, self).__init__(parent, *args, **kw)
        self.gsize = gsize
        self._grid = ItemGrid(self.NCOLS,
                              self.gsize+CellGraphicsItem.BOUNDARY)
        self._hdf = None

        scene = AfGraphicsScene()
        scene.setBackgroundBrush(QtCore.Qt.darkGray)
        self.setScene(scene)

    def updateRaster(self, gsize):
        self.gsize = gsize
        self._grid.colwidth = self.gsize + CellGraphicsItem.BOUNDARY

    def reorder(self):
        scaled_colwidth = self.transform().m11()*self._grid.colwidth
        col_count = math.floor(self.size().width()%scaled_colwidth)
        if self._grid.colCount() > col_count:
            self._grid.reorder(self.size().width()/self.transform().m11())
            # slow according to qt-doc
            ibr = self.scene().itemsBoundingRect()
            self.scene().setSceneRect(ibr)

    def resizeEvent(self, event):
        super(AfGraphicsView, self).resizeEvent(event)
        self.reorder()

    def wheelEvent(self, event):
        super(AfGraphicsView, self).wheelEvent(event)
        # self.reorder()

    def openFile(self, file_):
        self._hdf = HdfReader(file_, "r", cached=True)

        coord = dict()
        p = self.parent()
        p.plate.addItems(self._hdf.plateNames())
        coord["plate"] = p.plate.currentText()
        p.well.addItems(self._hdf.wellNames(coord))
        coord["well"] = p.well.currentText()
        p.site.addItems(self._hdf.siteNames(coord))
        p.region.addItems(self._hdf.regionNames())

    def loadItems(self, plate, well, site, region, size, nitems):
        assert isinstance(size, int)
        assert isinstance(nitems, int)

        coord = HdfCoord(plate, well, site, region)
        ftr_names = self._hdf.featureNames(region)
        nf = self._hdf.numberItems(coord)

        indices = np.random.randint(0, nf, nitems)
        for i, idx in enumerate(indices):
            item = self._hdf.loadItem(idx, coord, size)
            self.addItem(item.image, item.contour)
            self.itemLoaded.emit(i+1)
            QtGui.QApplication.processEvents()

    def clear(self):
        self._abort = True
        self.scene().clear()
        self.scene().setSceneRect(QtCore.QRectF())
        self._grid.reset()

    def addItem(self, gallery, cnt=None):

        citem = CellGraphicsItem()
        citem.setImage(array2qimage(gallery))
        if cnt is not None:
            citem.setContour(cnt)

        citem.setPos(*self._grid.newPos(citem))
        self.scene().addItem(citem)
