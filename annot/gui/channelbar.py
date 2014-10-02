"""
channelbar.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('ChannelBar', )

import math
import warnings
import numpy as np

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import QPointF
from collections import OrderedDict, defaultdict

from annot.config import AtConfig
from annot.gui.colorbutton import ColorButton
from annot.gui.painting import AtPainter
from annot.gui.contrast import AtEnhancerWidget


class ChannelBar(QtGui.QWidget):
    """ChannelBar is a layer between the import dialog and the viewer widget.
    It modifies the image drawn in the viewer i.e. it turns on/off the channels,
    enhances the contrast and sets the color table of the image."""

    newPixmap = QtCore.pyqtSignal(QtGui.QPixmap)
    newContourImage = QtCore.pyqtSignal(QtGui.QPixmap, "PyQt_PyObject")

    def __init__(self, parent, viewer, *args, **kw):
        super(ChannelBar, self).__init__(parent, *args, **kw)
        self._images = None
        self._contours = None
        self._channel_count = 0

        self.viewer = viewer
        vbox = QtGui.QVBoxLayout(self)
        self.gbox = QtGui.QGridLayout()
        cbox = QtGui.QVBoxLayout()
        self.enhancer = AtEnhancerWidget(self)
        self.enhancer.valuesUpdated.connect(self.updateImage)

        cbox.addWidget(self.enhancer)
        vbox.addLayout(self.gbox)
        vbox.addLayout(cbox)

        vbox.setContentsMargins(3, 3, 3, 3)
        self.gbox.setContentsMargins(0, 0, 0, 0)
        cbox.setContentsMargins(0, 0, 0, 0)

    def addChannels(self, n):
        self.clear()
        self._channel_count = n

        if n > 1:
            colors = lambda i: ColorButton.colors[i % len(ColorButton.colors)]
        else:
            colors = lambda i: ColorButton.white

        for i in xrange(n):
            cb = QtGui.QCheckBox("Channel %d" %(i+1))
            cb.setCheckState(QtCore.Qt.Checked)
            cb.stateChanged.connect(self.updateImage)
            cbtn  = ColorButton(colors(i))
            cbtn.colorChanged.connect(self.updateImage)
            self.gbox.addWidget(cb, i, 0)
            self.gbox.addWidget(cbtn, i, 1)
            self.enhancer.addChannel(cb.text())

    def setColor(self, name, color):

        chnames = self.allChannels()
        try:
            i = chnames.index(name)
        except ValueError:
            warnings.warn("can not set color for channel %s" %name)
        else:
            cb = self.widgetAt(i, 1)
            cb.setColor(QtGui.QColor(color))


    def activateChannels(self, channels):

        for i in xrange(self._channel_count):
            cb = self.widgetAt(i, 0)
            if cb.text() in channels:
                cb.setCheckState(QtCore.Qt.Checked)
            else:
                cb.setCheckState(QtCore.Qt.Unchecked)

    def widgetAt(self, row, column):
        return self.gbox.itemAtPosition(row, column).widget()

    def clear(self):
        self.enhancer.clear()
        for i in range(self.gbox.count()):
            item = self.gbox.takeAt(0)
            item.widget().close()

    def channelNames(self):
        cnames = list()
        for i in self.checkedChannels():
            cnames.append(self.widgetAt(i, 0).text())
        return cnames

    def colors(self):
        colors = dict()
        for i in xrange(self._channel_count):
            colors[self.widgetAt(i, 0).text()] = \
                self.widgetAt(i, 1).currentColor().name()
        return colors

    def checkedChannels(self):
        channels = OrderedDict()
        for i in xrange(self._channel_count):
            cb = self.widgetAt(i, 0)
            if cb.isChecked():
                channels[i] = cb.text()
        return channels

    def allChannels(self):
        return [self.widgetAt(i, 0).text() for i in xrange(self._channel_count)]

    def updateImage(self, dummy=None):

        if self._images is None:
            raise RuntimeError("No images set!")

        images = list()
        contours = dict()

 #      ccolor = AtConfig().contours_complementary_color

        for i, n in self.checkedChannels().iteritems():
            # converting the gray image to the color defined in the button
            color = self.widgetAt(i, 1).currentColor()
            image = self._images[i]
            lut = self.enhancer.lut_from_color(i, color, 256)
            image.setColorTable(lut)
            images.append(image)
            if self._contours is not None:
                # if ccolor:
                #     color = AtPainter.complementaryColor(color)
                contours[color] = self._contours[n]

        pixmap = AtPainter.blend(images)

        # sometimes qt segfaults when drawing polygons
        if AtConfig().draw_contours_in_pixmap:
            pixmap = AtPainter.drawContours(pixmap, contours)
            self.newContourImage.emit(pixmap, None)
        else:
            self.newContourImage.emit(pixmap, contours)

    def setImages(self, images, image_props=None):
        self._images = images

        if image_props is not None:
            self.enhancer.setImageProps(image_props)
        self.updateImage()

    def setContours(self, contours_dict):

        cnts = defaultdict(list)
        for contours in contours_dict.itervalues():
            # operate only on checked channels here, since there
            # no contours available for unchecked channels
            for cname in self.checkedChannels().itervalues():
                    polygon = QtGui.QPolygonF(
                        [QPointF(*c) for c in contours[cname]])
                    cnts[cname].append(polygon)

        self._contours = cnts
        self.updateImage()

    def clearContours(self):
        self._contours = None

    def drawRectangles(self, centers, gsize, isize):
        hsize = int(math.floor(gsize/2.0))
        # left, top, width, height
        centers = np.array([(x-hsize, y-hsize) for x, y in centers])
        centers [:, 0] = np.clip(centers[:, 0], 0, isize[0]-gsize)
        centers [:, 1] = np.clip(centers[:, 1], 0, isize[1]-gsize)

        rects = tuple([(x, y, gsize, gsize) for x, y in centers])
        self.viewer.drawRects(rects)

    def contourImage(self, images, contours_dict):
        """Combines setImage and setContours but updates viewer only once."""
        self._images = images
        self.setContours(contours_dict)
