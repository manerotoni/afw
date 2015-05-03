"""
slider.py

Custom QSlider that emit additional "newValue" signal.
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from PyQt5 import QtWidgets
from PyQt5 import QtCore

class AtSlider(QtWidgets.QSlider):

    newValue = QtCore.pyqtSignal()

    def wheelEvent(self, event):
        super(AtSlider, self).wheelEvent(event)
        # important! first call super, then emit signal
        self.newValue.emit()
