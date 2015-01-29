"""
featuregroups.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtFeatureGroupsWidget", )

from os.path import splitext

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

from annot.segmentation.channelname import ChannelName as cn


class AtFeatureGroupsWidget(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(AtFeatureGroupsWidget, self).__init__(*args, **kw)
        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addStretch()
        self.vbox.setContentsMargins(2, 2, 2, 2)
        self._channels = None

    def setChannelNames(self, channel_names):
        self.clear()

        self._channels = channel_names
        for chn in channel_names:
            fgw = AtChannelFeatureGroupsWidget(chn, self)
            self.vbox.insertWidget(self.vbox.count()-1, fgw)
            setattr(self, chn.lower(), fgw)

    def clear(self):
        for i in xrange(self.vbox.count()-1):
            item = self.vbox.takeAt(0)
            item.widget().close()


class AtChannelFeatureGroupsWidget(QtGui.QWidget):

    selectionChanged = QtCore.pyqtSignal(int)

    BRIGHTNESS = 2
    SHAPE      = 2<<1
    TEXTURE    = 2<<2
    SIZE       = 2<<3

    def __init__(self, title, *args, **kw):
        super(AtChannelFeatureGroupsWidget, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        uic.loadUi(uifile, self)
        self.setTitle(cn.display(title))

        self.brightness.stateChanged.connect(self.onStateChanged)
        self.shape.stateChanged.connect(self.onStateChanged)
        self.texture.stateChanged.connect(self.onStateChanged)
        self.size_.stateChanged.connect(self.onStateChanged)

    def setTitle(self, title):
        self.gbox.setTitle(title)

    def onStateChanged(self, dummy=None):
        groups = 0
        if self.brightness.isChecked():
            groups = groups|self.BRIGHTNESS

        if self.shape.isChecked():
            groups = groups|self.SHAPE

        if self.texture.isChecked():
            groups = groups|self.TEXTURE

        if self.size_.isChecked():
            groups = groups|self.SIZE

        print groups
        self.selectionChanged.emit(groups)
