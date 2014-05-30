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


class ChannelBar(QtGui.QWidget):

    newPixmap = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, *args, **kw):
        super(ChannelBar, self).__init__(*args, **kw)
        vbox = QtGui.QVBoxLayout(self)

        self.gbox = QtGui.QGridLayout()
        cbox = QtGui.QVBoxLayout()
        self.enhancer = AfEnhancerWidget(self)
        self.enhancer.valuesUpdated.connect(self.updateImage)

        cbox.addWidget(self.enhancer)

        vbox.addLayout(self.gbox)
        vbox.addLayout(cbox)

        vbox.setContentsMargins(3, 3, 3, 3)
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
        for i in range(self.gbox.count()):
            item = self.gbox.takeAt(0)
            item.widget().close()

    def channelNames(self):
        cnames = list()
        for i in xrange(self.gbox.rowCount()):
            cnames.append(self.widgetAt(i, 0).text())
        return cnames

    def colors(self):
        colors = dict()
        for i in xrange(self.gbox.rowCount()):
            colors[self.widgetAt(i, 0).text()] = \
                self.widgetAt(i, 1).currentColor().name()
        return colors

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
            lut = self.enhancer.lut_from_color(i, color, 256)
            image.setColorTable(lut)
            images.append(image)

        pixmap = AfPainter.blend(images)
        self.newPixmap.emit(pixmap)

    def setImages(self, images, image_props=None):
        self._images = images

        if image_props is not None:
            self.enhancer.setImageProps(image_props)
        self.updateImage()
