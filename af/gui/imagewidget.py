"""
imageviewer.py

QGraphicsView widget with pan ans zoom features (ctrl + mouse)
and a minimalistic context menu.
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ["ImageWidget", "ImageViewer"]

from PyQt4 import QtGui
from PyQt4.QtCore import Qt


class ImageWidget(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(ImageWidget, self).__init__(*args, **kw)
        self.resize(512, 512)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding,
                           QtGui.QSizePolicy.Expanding)

        self.iview = ImageViewer(self)
        box = QtGui.QHBoxLayout(self)
        box.setContentsMargins(0, 0, 0, 0)
        box.addWidget(self.iview)

    def showImage(self, image):
        assert isinstance(image, QtGui.QImage)
        self.iview.showPixmap(QtGui.QPixmap.fromImage(image))

    def showPixmap(self, pixmap):
        assert isinstance(pixmap, QtGui.QPixmap)
        self.iview.showPixmap(pixmap)


class ImageViewer(QtGui.QGraphicsView):

    def __init__(self, *args, **kw):
        super(ImageViewer, self).__init__(*args, **kw)
        self.setScene(QtGui.QGraphicsScene())
        self.setBackgroundBrush(Qt.darkGray)

        self.setDragMode(self.NoDrag)
        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setResizeAnchor(self.AnchorViewCenter)
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(self.SmartViewportUpdate)

        self._pixmap = QtGui.QGraphicsPixmapItem()
        self._pixmap.setShapeMode(QtGui.QGraphicsPixmapItem.BoundingRectShape)
        # self._pixmap.setTransformationMode(Qt.SmoothTransformation)
        self._polygonitems = list()
        self.scene().addItem(self._pixmap)
        self.setToolTip("ctrl+mouse to pan/zoom")

        self.createActions()
        self.createContextMenu()
        self.actionMaximize.setChecked(True)

    def createContextMenu(self):
        self.context_menu = QtGui.QMenu(self)
        self.context_menu.addAction(self.actionOrigSize)
        self.context_menu.addAction(self.actionExpand)
        self.context_menu.addAction(self.actionMaximize)

    def createActions(self):
        self.actionOrigSize = QtGui.QAction(
            "&original size", self, triggered=self.origsize)
        self.actionExpand = QtGui.QAction("&expand to window", self,
                checkable=True, triggered=self.expand)
        self.actionMaximize = QtGui.QAction("&fit in window", self,
                checkable=True, triggered=self.maximize)

        actiongrp = QtGui.QActionGroup(self)
        self.actionExpand.setActionGroup(actiongrp)
        self.actionMaximize.setActionGroup(actiongrp)

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
            QtGui.QApplication.setOverrideCursor(
                QtGui.QCursor(Qt.OpenHandCursor))
        elif event.key() == Qt.Key_R:
            self.scaleReset()
        elif event.key() == Qt.Key_M:
            self.maximize()
        elif event.key() == Qt.Key_F:
            self.expand()

        super(ImageViewer, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            QtGui.QApplication.restoreOverrideCursor()
        super(ImageViewer, self).keyReleaseEvent(event)

    def mousePressEvent(self, event):

        if (event.button() == Qt.LeftButton and \
                event.modifiers() == Qt.ControlModifier):
            self.setDragMode(self.ScrollHandDrag)
            QtGui.QApplication.setOverrideCursor(
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
            QtGui.QApplication.restoreOverrideCursor()
        super(ImageViewer, self).mousePressEvent(event)

    def wheelEvent(self, event):

        if event.modifiers() == Qt.ControlModifier:
            self.actionExpand.setChecked(False)
            self.actionMaximize.setChecked(False)

            if event.delta() > 0:
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
            if isinstance(item, QtGui.QGraphicsPolygonItem):
                self.scene().removeItem(item)


    def contourImage(self, pixmap, contours_dict=None):
        self.showPixmap(pixmap)
        self.clearPolygons()

        if contours_dict is not None:
            for color, contours in contours_dict.iteritems():
                for contour in contours:
                    pen = QtGui.QPen()
                    pen.setColor(color)
                    self.scene().addPolygon(contour, pen=pen)


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    imagedlg = ImageWidget()
    imagedlg.showImage(QtGui.QImage(sys.argv[1]))
    imagedlg.show()
    sys.exit(app.exec_())
