"""
painting.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from PyQt4 import QtGui
from PyQt4.QtCore import Qt


class AfPainter(object):

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

    def drawContours(self, contours):
        pass
