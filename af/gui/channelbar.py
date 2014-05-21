"""
channelbar.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('ChannelBar', )


import numpy as np
from PyQt4 import QtGui
from PyQt4 import QtCore
from af.gui.colorbutton import ColorButton
from af.gui.painting import AfPainter
from af.gui.contrast import AfEnhancerWidget


def lut_from_color(color, ncolors):
    """Create a colormap from a single color e.g. red and return
    a list of qRgb instances.
    """
    lut = np.zeros((ncolors, 3), dtype=int)
    for i, col in enumerate((color.red(), color.green(), color.blue())):
        lut[: , i] = np.array(range(ncolors)) / (ncolors - 1.0) * col

    return [QtGui.qRgb(r, g, b) for r, g, b in lut]


class ChannelBar(QtGui.QWidget):

    newPixmap = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, *args, **kw):
        super(ChannelBar, self).__init__(*args, **kw)
        vbox = QtGui.QVBoxLayout(self)

        self.gbox = QtGui.QGridLayout()
        cbox = QtGui.QVBoxLayout()
        self.enhancer = AfEnhancerWidget(self)

        cbox.addWidget(self.enhancer)

        vbox.addLayout(self.gbox)
        vbox.addLayout(cbox)

        vbox.setContentsMargins(0, 0, 0, 0)
        self.gbox.setContentsMargins(0, 0, 0, 0)
        cbox.setContentsMargins(0, 0, 0, 0)

        self._images = None

    def addChannels(self, n):
        self.clear()
        for i in xrange(n):
            cb = QtGui.QCheckBox("Channel %d" %(i+1))
            cb.setCheckState(QtCore.Qt.Checked)
            cb.stateChanged.connect(self.updateImage)
            cbtn  = ColorButton()
            cbtn.colorChanged.connect(self.updateImage)
            self.gbox.addWidget(cb, i, 0)
            self.gbox.addWidget(cbtn, i, 1)
            self.enhancer.addChannel(cb.text())

    def widgetAt(self, row, column):
        return self.gbox.itemAtPosition(row, column).widget()

    def clear(self):
        self.enhancer.clear()
        for i in xrange(self.gbox.rowCount()):
            for j in xrange(self.gbox.columnCount()):
                item  = self.gbox.itemAtPosition(i, j)
                if item is not None:
                    self.gbox.removeWidget(item.widget())
                    item.widget().close()


    def checkedChannels(self):
        cidx = list()
        for i in xrange(self.gbox.rowCount()):
            cb = self.widgetAt(i, 0)
            if cb.isChecked():
                cidx.append(i)
        return cidx

    def updateImage(self, dummy=None):
        if self._images is None:
            raise RuntimeError("No images set!")

        images = list()
        for i in self.checkedChannels():
            # converting the gray image to the color defined in the button
            color = self.widgetAt(i, 1).currentColor()
            image = self._images[i]
            lut = lut_from_color(color, image.depth()*8)
            image = image.convertToFormat(image.Format_Indexed8, lut)
#            image = self.enhancer.enhanceImage(i, image)
            images.append(image)

        pixmap = AfPainter.blend(images)
        self.newPixmap.emit(pixmap)

    def setImages(self, images):
        self._images = images
        self.updateImage()
