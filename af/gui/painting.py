"""
painting.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy as np
from PyQt4 import QtGui
from PyQt4.QtCore import Qt


class AfPainter(object):

    @staticmethod
    def lut_from_color(color, ncolors):
        """Create a colormap from a single color e.g. red and return
        a list of qRgb instances.
        """

        lut = np.zeros((ncolors, 3), dtype=int)
        for i, col in enumerate((color.red(), color.green(), color.blue())):
            lut[: , i] = np.array(range(ncolors)) / (ncolors - 1.0) * col

        return [QtGui.qRgb(r, g, b) for r, g, b in lut]

    @staticmethod
    def blend(images):
        """Merging arb. number of gray images to one color image"""

        try:
            pixmap = QtGui.QPixmap(images[0].width(), images[0].height())
        except IndexError:
            pixmap = QtGui.QPixmap(512, 512)

        pixmap.fill(Qt.black)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_Lighten)

        for image in images:
            painter.drawImage(0, 0, image)
        painter.end()
        return pixmap

    @staticmethod
    def drawContours(pixmap, polygons):
        assert isinstance(pixmap, QtGui.QPixmap)

        painter = QtGui.QPainter(pixmap)
        pen = QtGui.QPen()
        painter.setBrush(Qt.NoBrush)

        for color, polygons in polygons.iteritems():
            pen.setColor(color)
            painter.setPen(pen)
            for polygon in polygons:
                painter.drawPolygon(polygon)

        painter.end()

        return pixmap

    @staticmethod
    def complementaryColor(color):
        r = 255 - color.red()
        g = 255 - color.green()
        b = 255 - color.blue()

        if r == g == b:
            return QtGui.QColor(255, 255, 255)
        else:
            return QtGui.QColor(r, g, b)
