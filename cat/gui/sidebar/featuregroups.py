"""
featuregroups.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtFeatureGroupsWidget", )

from os.path import splitext

from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import Qt


from .feature_tables import FeatureTables
from cat.segmentation.channelname import ChannelName as cn


class AtFeatureGroupsWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.pyqtSignal(tuple)

    def __init__(self, *args, **kw):
        super(AtFeatureGroupsWidget, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        uic.loadUi(uifile, self)

        self.vbox.addStretch()
        self.vbox.setContentsMargins(2, 2, 2, 2)
        self._channels = None

    def _iterGroups(self):
        for i in xrange(self.vbox.count()-1):
            yield self.vbox.itemAt(i).widget()

    def setChannelNames(self, channel_names):
        self.clear()

        self._channels = channel_names
        for chn in channel_names:
            fgw = AtChannelFeatureGroupsWidget(chn, self)
            self.vbox.insertWidget(self.vbox.count()-1, fgw)
            fgw.selectionChanged.connect(self.onSelectionChanged)
            setattr(self, chn.lower(), fgw)

    def clear(self):
        for i in xrange(self.vbox.count()-1):
            item = self.vbox.takeAt(0)
            item.widget().close()

    def onSelectionChanged(self):
        feature_names = list()
        for widget in self._iterGroups():
            feature_names.extend(widget.currentFeatureNames())
        self.selectionChanged.emit(tuple(feature_names))


class AtChannelFeatureGroupsWidget(QtWidgets.QWidget):

    selectionChanged = QtCore.pyqtSignal()

    def __init__(self, title, *args, **kw):
        super(AtChannelFeatureGroupsWidget, self).__init__(*args, **kw)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.gbox = QtWidgets.QGroupBox(self)

        self.gbox.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.gbox)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.gbox.setTitle(cn.display(title))

        self._table = FeatureTables.Cecog
        for group, names in self._table.iteritems():
            self.addFeatureGroup(group, names)

    def addFeatureGroup(self, group, feature_names):
        checkbox = QtWidgets.QCheckBox(group)
        checkbox.setCheckState(QtCore.Qt.Checked)
        checkbox.stateChanged.connect(self.onStateChanged)
        self.gbox.layout().addWidget(checkbox)

    def currentFeatureNames(self):
        features = list()
        prefix = cn.abreviate(self.gbox.title())
        layout = self.gbox.layout()
        for i in xrange(layout.count()):
            cb = layout.itemAt(i).widget()
            if cb.isChecked():
                ftrs = ("%s-%s" %(prefix, f) for f in self._table[cb.text()])
                features.extend(ftrs)
        return features

    def onStateChanged(self, dummy=None):
        self.selectionChanged.emit()
