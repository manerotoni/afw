"""
colorbutton.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ( 'ColorButton', )


from itertools import cycle
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

default_colors = (Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta,
                  Qt.yellow, Qt.darkRed, Qt.darkGreen, Qt.darkBlue,
                  Qt.darkCyan, Qt.darkMagenta, Qt.darkYellow)

class ColorButton(QtGui.QPushButton):

    colorChanged = QtCore.pyqtSignal(QtGui.QColor)
    _default_colors = cycle(default_colors)

    def __init__(self, *args, **kw):
        super(ColorButton, self).__init__(*args, **kw)
        color = self._default_colors.next()
        self.setMaximumWidth(24)
        self.setMaximumHeight(16)
        self.setColor(QtGui.QColor(color))
        self.clicked.connect(self.onClicked)

    def close(self):
        self._setDefaultColors()

    @classmethod
    def _setDefaultColors(cls):
        cls._default_colors = cycle(default_colors)

    def setColor(self, color):
        self._current_color = color
        self.setStyleSheet("background-color: rgb(%d, %d, %d)" %
                           (color.red(), color.green(), color.blue()))
        self.colorChanged.emit(color)

    def onClicked(self):
        dlg = QtGui.QColorDialog(self)

        if self._current_color is not None:
            dlg.setCurrentColor(self._current_color)

        if dlg.exec_():
            col = dlg.currentColor()
            self.setColor(col)
            self.colorChanged.emit(col)
