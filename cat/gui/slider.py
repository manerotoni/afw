"""
slider.py

Custom QSlider that emit additional "newValue" signal.
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from PyQt4 import QtGui
from PyQt4 import QtCore

class AtSlider(QtGui.QSlider):

    newValue = QtCore.pyqtSignal()

    def wheelEvent(self, event):
        super(AtSlider, self).wheelEvent(event)
        # important! first call super, then emit signal
        self.newValue.emit()
