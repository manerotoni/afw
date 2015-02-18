"""
colorbutton.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ( 'ColorButton', )


from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import Qt


class ColorButton(QtGui.QPushButton):

    colorChanged = QtCore.pyqtSignal(QtGui.QColor)
    white = Qt.white
    colors = (Qt.red, Qt.green, Qt.blue, Qt.cyan, Qt.magenta,
              Qt.yellow, Qt.darkRed, Qt.darkGreen, Qt.darkBlue,
              Qt.darkCyan, Qt.darkMagenta, Qt.darkYellow)

    def __init__(self, color, *args, **kw):
        super(ColorButton, self).__init__(*args, **kw)
        self.setMaximumWidth(24)
        self.setMaximumHeight(16)
        self.setColor(QtGui.QColor(color))
        self.clicked.connect(self.onClicked)

    def close(self):
        super(ColorButton, self).close()

    def setColor(self, color):
        self._current_color = color
        self.setStyleSheet("ColorButton {background-color: rgb(%d, %d, %d)}" %
                           (color.red(), color.green(), color.blue()))
        self.colorChanged.emit(color)

    def currentColor(self):
        return self._current_color

    def onClicked(self):
        dlg = QtGui.QColorDialog(self)

        if self._current_color is not None:
            dlg.setCurrentColor(self._current_color)

        if dlg.exec_():
            col = dlg.currentColor()
            self.setColor(col)
            self.colorChanged.emit(col)
