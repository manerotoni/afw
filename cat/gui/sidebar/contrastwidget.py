"""
contrastwidget.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtContrastWidget", )

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QCursor


from cat.gui.contrast import AtEnhancerWidget
from cat.segmentation import ChannelName as cn


class AtContrastWidget(QtWidgets.QWidget):

    def __init__(self, parent, tileview, featuredlg=None, *args, **kw):
        super(AtContrastWidget, self).__init__(parent)
        self.tileview = tileview
        self.featuredlg = featuredlg
        self.parent = parent
        self.colors = None

        vbox = QtWidgets.QVBoxLayout(self)
        self.enhancer= AtEnhancerWidget(self)
        vbox.addWidget(self.enhancer)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.enhancer.sliderReleased.connect(self.enhanceContrast)

    def setChannelNames(self, channels, colors):
        self.colors = colors
        self.enhancer.clear()
        for channel in channels:
            self.enhancer.addChannel(cn.display(channel), no_auto_button=True)

    def enhanceContrast(self):
        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            i = self.enhancer.currentChannelIndex()
            color = QtGui.QColor(self.colors[i])
            lut = self.enhancer.lut_from_color(i, color, 256)
            for item in self.tileview.items:
                item.enhancePixmap(i, lut)
        finally:
            QApplication.restoreOverrideCursor()
