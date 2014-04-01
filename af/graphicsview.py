"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

__all__ = ("AfGraphicsView", )

import math
from qimage2ndarray import array2qimage
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

from af.itemgrid import ItemGrid
from af.cellitem import CellGraphicsItem
from af.graphicsscene import AfGraphicsScene
from af.hdfio import HdfReader


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

    GSIZE = 50
    NCOLS = 15

    def __init__(self, *args, **kw):
        super(AfGraphicsView, self).__init__(*args, **kw)
        self._grid = ItemGrid(self.NCOLS, self.GSIZE+4)
        self._hdf = None

        scene = AfGraphicsScene()
        scene.setBackgroundBrush(QtCore.Qt.darkGray)
        self.setScene(scene)

    def resizeEvent(self, event):

        scaled_colwidth = self.transform().m11()*self._grid.colwidth
        col_count = math.floor(event.size().width()%scaled_colwidth)
        if self._grid.colCount() > col_count:
            self._grid.reorder(event.size().width()/self.transform().m11())
#            self.ensureVisible(self.sceneRect(), 10, 10)
            # slow according to qt-doc
            ibr = self.scene().itemsBoundingRect()
            self.scene().setSceneRect(ibr)
        super(MouseWheelView, self).resizeEvent(event)


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

    def loadItems(self, plate, well, site, region):
        for gal in self._hdf.iterEventGallery(plate, well, site, region,
                                              size=self.GSIZE):
            self.addItem(gal)
            QtGui.QApplication.processEvents()

    def clear(self):
        self._abort = True
        self.scene().clear()
        self._grid.reset()

    def addItem(self, gallery):
        pitem = CellGraphicsItem()
        pitem.setImage(array2qimage(gallery))
        pitem.setPos(*self._grid.newPos(pitem))
        self.scene().addItem(pitem)
