"""
imageviewer.py

QGraphicsView widget with pan and zoom features (CTRL + mouse)
and a minimalistic context menu.
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("ImageWidget", "ImageViewer")

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt


class ImageWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kw):
        super(ImageWidget, self).__init__(*args, **kw)
        self.resize(512, 512)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)

        self.iview = ImageViewer(self)
        box = QtWidgets.QHBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.addWidget(self.iview)

    def showImage(self, image):
        assert isinstance(image, QtWidgets.QImage)
        self.iview.showPixmap(QtGui.QPixmap.fromImage(image))

    def showPixmap(self, pixmap):
        assert isinstance(pixmap, QtGui.QPixmap)
        self.iview.showPixmap(pixmap)


class ImageViewer(QtWidgets.QGraphicsView):

    ContourWidth = 0.0

    def __init__(self, *args, **kw):
        super(ImageViewer, self).__init__(*args, **kw)
        self.setScene(QtWidgets.QGraphicsScene())
        self.setBackgroundBrush(Qt.darkGray)

        self.setDragMode(self.NoDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorViewCenter)
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(self.SmartViewportUpdate)

        self._pixmap = QtWidgets.QGraphicsPixmapItem()
        self._pixmap.setShapeMode(
            QtWidgets.QGraphicsPixmapItem.BoundingRectShape)

        self._polygonitems = list()
        self.scene().addItem(self._pixmap)
        self.setToolTip("CTRL+Mouse to pan/zoom")

        self.createActions()
        self.createContextMenu()
        self.actionMaximize.setChecked(True)

    def createContextMenu(self):
        self.context_menu = QtWidgets.QMenu(self)
        self.context_menu.addAction(self.actionOrigSize)
        self.context_menu.addAction(self.actionExpand)
        self.context_menu.addAction(self.actionMaximize)
        self.context_menu.addAction(self.actionZoomIn)
        self.context_menu.addAction(self.actionZoomOut)

    def createActions(self):

        self.actionOrigSize = QtWidgets.QAction(
            "&Original Size", self, triggered=self.origsize)
        self.actionExpand = QtWidgets.QAction("&Expand Image", self,
                checkable=True, triggered=self.expand)
        self.actionMaximize = QtWidgets.QAction("&Maximize Image", self,
                checkable=True, triggered=self.maximize)

        self.actionZoomIn = QtWidgets.QAction("Zoom in (+)", self,
                checkable=False, triggered=self.zoomIn)

        self.actionZoomOut = QtWidgets.QAction("Zoom out (-)", self,
                checkable=False, triggered=self.zoomOut)

        actiongrp = QtWidgets.QActionGroup(self)
        self.actionExpand.setActionGroup(actiongrp)
        self.actionMaximize.setActionGroup(actiongrp)

    def zoomOut(self):
        self.actionMaximize.setChecked(False)
        self.actionExpand.setChecked(False)
        self.actionOrigSize.setChecked(False)
        self.scale(0.9, 0.9)

    def zoomIn(self):
        self.actionMaximize.setChecked(False)
        self.actionExpand.setChecked(False)
        self.actionOrigSize.setChecked(False)
        self.scale(1.1, 1.1)

    @property
    def scalefactor(self):
        return self.transform().m11()

    def scale(self, sx, sy):
        if sx*self.scalefactor:
            super(ImageViewer, self).scale(sx, sy)

    def origsize(self):
        self.actionExpand.setChecked(False)
        self.actionMaximize.setChecked(False)
        self.resetTransform()

    def maximize(self):
        self.actionExpand.setChecked(False)
        self.fitInView(self._pixmap, mode=Qt.KeepAspectRatio)

    def expand(self):
        self.actionMaximize.setChecked(False)
        self.fitInView(self._pixmap, mode=Qt.IgnoreAspectRatio)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.setCursor(QtGui.QCursor(Qt.OpenHandCursor))
        elif event.key() == Qt.Key_O:
            self.origsize()
        elif event.key() == Qt.Key_M:
            self.maximize()
        elif event.key() == Qt.Key_F:
            self.expand()
        elif event.key() == Qt.Key_Plus:
            self.zoomIn()
        elif event.key() == Qt.Key_Minus:
            self.zoomOut()

        super(ImageViewer, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.unsetCursor()
        super(ImageViewer, self).keyReleaseEvent(event)

    def mousePressEvent(self, event):

        if (event.button() == Qt.LeftButton and \
                event.modifiers() == Qt.ControlModifier):
            self.setDragMode(self.ScrollHandDrag)
            self.setCursor(
                QtGui.QCursor(Qt.ClosedHandCursor))

        super(ImageViewer, self).mousePressEvent(event)

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def resizeEvent(self, event):
        if self.actionExpand.isChecked():
            self.expand()
        elif self.actionMaximize.isChecked():
            self.maximize()

        super(ImageViewer, self).resizeEvent(event)

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.setDragMode(self.NoDrag)
            if event.modifiers() == Qt.ControlModifier:
                self.setCursor(QtGui.QCursor(Qt.OpenHandCursor))
            else:
                self.unsetCursor()
        super(ImageViewer, self).mousePressEvent(event)

    def wheelEvent(self, event):

        if event.modifiers() == Qt.ControlModifier:
            self.actionExpand.setChecked(False)
            self.actionMaximize.setChecked(False)

            if event.angleDelta().y() > 0:
                factor = 1.1
            else:
                factor = 0.9
            self.scale(factor, factor)

    def showPixmap(self, pixmap):
        self._pixmap.setPixmap(pixmap)

        if self.actionExpand.isChecked():
            self.expand()
        elif self.actionMaximize.isChecked():
            self.maximize()

    def clearPolygons(self):
        items = self.scene().items()
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsPolygonItem):
                self.scene().removeItem(item)

    def clearRects(self):
        items = self.scene().items()
        for item in items:
            if isinstance(item, QtWidgets.QGraphicsRectItem):
                self.scene().removeItem(item)

    def contourImage(self, pixmap, contours_dict=None):
        self.showPixmap(pixmap)
        self.clearPolygons()

        if contours_dict is not None:
            for color, contours in contours_dict.iteritems():
                for contour in contours:
                    pen = QtGui.QPen()
                    pen.setColor(color)
                    pen.setWidth(self.ContourWidth)
                    self.scene().addPolygon(contour, pen=pen)

    def drawRects(self, rects):
        self.clearRects()

        for x, y, w, h in rects:
            pen = QtGui.QPen()
            pen.setColor(Qt.white)
            pen.setStyle(Qt.DotLine)

            brush = QtGui.QBrush()
            brush.setStyle(Qt.NoBrush)

            self.scene().addRect(x, y, w, h, pen=pen, brush=brush)

if __name__ == '__main__':

    import sys
    app = QtWidgets.QApplication(sys.argv)
    imagedlg = ImageWidget()
    imagedlg.showImage(QtWidgets.QImage(sys.argv[1]))
    imagedlg.show()
    sys.exit(app.exec_())
