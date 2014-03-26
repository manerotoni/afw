"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

__all__ = ("GraphicsTileView", "GridScene")

import sys
import argparse
from qimage2ndarray import array2qimage
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import cellh5
from itemgrid import ItemGrid
from cellitem import CellGraphicsItem


class GridScene(QtGui.QGraphicsScene):
    """GraphicsScene with customized selection functionality

    -) double-click -> selects a single item, unselects all other items
    -) Ctrl-button + left mouse buuton -> selects all items the mouse moved over
    -) Ctrl-button + mouse click -> selects the item clicked,
       keeps previous selection
    """

    def __init__(self, *args, **kw):
        super(GridScene, self).__init__(*args, **kw)
        self._multiselect = False
        self._selector = None

    def mouseMoveEvent(self, event):

        if self._multiselect:
            plg = self._selector.polygon()
            plg += event.scenePos()
            self._selector.setPolygon(plg)

        try:
            item = self.items(event.scenePos())[-1]
        except IndexError:
            item = None

        # print items
        # from PyQt4.QtCore import pyqtRemoveInputHook; pyqtRemoveInputHook()
        # import pdb; pdb.set_trace()


        if (event.modifiers() == QtCore.Qt.ControlModifier and
            item is not None and
            self._multiselect):
            item.setSelected(True)
        else:
            super(GridScene, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton:
            self._multiselect = True

        if event.button() == QtCore.Qt.RightButton:
            return
        elif event.modifiers() == QtCore.Qt.ControlModifier:
            pen = QtGui.QPen()
            pen.setColor(QtCore.Qt.white)
            pen.setWidth(3)
            polygon = QtGui.QPolygonF()
            self._selector = self.addPolygon(polygon, pen)

            super(GridScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._multiselect = False

        if self._selector is not None:
            self.removeItem(self._selector)
            self._selector = None

        super(GridScene, self).mouseReleaseEvent(event)


    def paint(self, painter, option, widget):
        print "foobar"
        super(GridScene, self).paint(painter, option, widget)


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


class GraphicsTileView(MouseWheelView):

    GSIZE = 50
    NCOLS = 10

    def __init__(self,  file_, region, *args, **kw):
        super(GraphicsTileView, self).__init__(*args, **kw)

        self.file = file_
        self.region = region
        self._grid = ItemGrid(self.NCOLS, self.GSIZE+4)

        scene = GridScene()
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
        events = pos.get_events().flatten()[:30]
        for event in events:
            yield pos.get_gallery_image(event, region, size)



if __name__ == '__main__':


    parser = argparse.ArgumentParser(\
        description='Test script for tiled graphicview widget')
    parser.add_argument('file', help='hdf file to load')
    parser.add_argument('--region', help="segmentation region",
                        default="primary__primary")

    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    tileview = GraphicsTileView(args.file, args.region)
    tileview.show()
    sys.exit(app.exec_())
