"""
channelbar.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('ChannelBar', )

from PyQt4 import QtGui
from af.gui.colorbutton import ColorButton


class ChannelBar(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(ChannelBar, self).__init__(*args, **kw)
        gbox = QtGui.QGridLayout(self)
        self.setLayout(gbox)

    def addChannels(self, n):
        self.clear()
        for i in xrange(n):
            cb = QtGui.QCheckBox("Channel %d" %(i+1))
            cbtn  = ColorButton()
            self.layout().addWidget(cb, i, 0)
            self.layout().addWidget(cbtn, i, 1)

    def widgetAt(self, row, column):
        return self.layout().itemAtPosition(row, column).widget()

    def clear(self):
        for i in xrange(self.layout().rowCount()):
            for j in xrange(self.layout().columnCount()):
                item  = self.layout().itemAtPosition(i, j)
                if item is not None:
                    self.layout().removeWidget(item.widget())
                    item.widget().close()

    def checkedChannels(self):
        cidx = list()
        for i in xrange(self.layout().rowCount()):
            cb = self.widgetAt(i, 0)
            if cb.isChecked():
                cidx.append(i)
        return cidx
