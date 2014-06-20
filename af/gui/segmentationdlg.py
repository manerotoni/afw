"""
segmentationdlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('SegmentationDialog', )

import sys
from collections import OrderedDict
from os.path import splitext, join, dirname

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from cecog import ccore
from af.gui.featurebox import FeatureBox
from af.segmentation import PrimaryParams, ExpansionParams

class ChLabel(QtGui.QLabel):

    def __init__(self, *args, **kw):
        super(ChLabel, self).__init__(*args, **kw)
        self.setAlignment(Qt.AlignHCenter|Qt.AlignRight)


class ExpansionWidget(QtGui.QGroupBox):

    def __init__(self, *args, **kw):
        super(ExpansionWidget, self).__init__(*args, **kw)
        uic.loadUi(join(dirname(__file__), "expansionregion.ui"), self)

    def setValue(self, value):
        self.spinBox.setValue(value)

    def value(self):
        return self.spinBox.value()

    def params(self):
        return ExpansionParams(
            ccore.SrgType.KeepContours, None, 0, self.value(), 0)


class SegmentationDialog(QtGui.QWidget):

    _ncols = 3

    NAME = 0
    SEGMENTATION = 1
    FEATURES = 2

    def __init__(self, *args, **kw):
        super(SegmentationDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowFlags(Qt.Window)
        # row count (rowCount from gridlayout is not reliable!)
        self._rcount = 1

        self.pchannel.currentIndexChanged[str].connect(self.onChannelChanged)

    def closeEvent(self, event):
        print "pre"
        super(SegmentationDialog, self).closeEvent(event)
        print "post"

    def onChannelChanged(self, channel):

        # determine the missing/ old channel of the combobox
        missing = [self.pchannel.itemText(i)
                   for i in xrange(self.pchannel.count())]
        for i in xrange(1, self._rcount, 1):
            missing.remove(self.widgetAt(i, self.NAME).text())

        for i in xrange(1, self._rcount, 1):
            widget = self.widgetAt(i, self.NAME)
            if widget.text() == channel:
                widget.setText(missing[0])


    def addExpandedRegion(self, name):
        expw = ExpansionWidget(self)
        ftrbox = FeatureBox(self)

        expw.setValue(expw.value()+ self._rcount)
        self.regionBox.addWidget(ChLabel(name), self._rcount, self.NAME)
        self.regionBox.addWidget(expw, self._rcount, self.SEGMENTATION)
        self.regionBox.addWidget(ftrbox, self._rcount, self.FEATURES)
        self._rcount += 1

    def _rowIndexOfRegion(self, region):
        rows = range(self._rcount)
        return [self.widgetAt(r, self.NAME).text() for r in rows].index(region)

    def widgetAt(self, row, column):
        return self.regionBox.itemAtPosition(row, column).widget()

    def clearRegions(self):
        for i in range(self.regionBox.count()-self._ncols):
            item = self.regionBox.takeAt(3)
            item.widget().deleteLater()
            del item
        self._rcount = 1

    def deleteRegion(self, region):

        ri = self._rowIndexOfRegion(region)
        idx = self._ncols*ri - 1
        for i in range(self._ncols):
            item = self.regionBox.takeAt(idx+1)
            item.widget().deleteLater()
            del item
        self._rcount -= 1

        self.pchannel.removeItem(self.pchannel.findText(region))

    def setRegions(self, names):
        self.clearRegions()
        self.pchannel.clear()
        for i, name in enumerate(names):
            if i > 0 : # assuming the first item is for the primary segmentation
                self.addExpandedRegion(name)
            else:
                self.pchannel.addItems(names)
                self.pchannel.setCurrentIndex(0)

    def _primaryParams(self):
        return PrimaryParams(self.meanRadius.value(),
                             self.windowSize.value(),
                             self.minContrast.value(),
                             self.removeBorderObjects.isChecked(),
                             self.fillHoles.isChecked())

    def segmentationParams(self):
        sparams = OrderedDict()

        for i in xrange(self._rcount):
            if i == 0:
                name = self.pchannel.currentText()
                sparams[name] = self._primaryParams()
            else:
                name = self.widgetAt(i, self.NAME).text()
                sparams[name] = self.widgetAt(i, self.SEGMENTATION).params()
        return sparams

    def featureGroups(self):
        fgroups = dict()
        for i in xrange(self._rcount):
            try:
                name = self.widgetAt(i, self.NAME).text()
            except AttributeError:
                name = self.pchannel.currentText()
            fgroups[name] = self.widgetAt(i, self.FEATURES).featureGroups()
        return fgroups


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sd = SegmentationDialog()
    sd.setRegions(["Channel 1", "Channel 2"])
    sd.show()

    # sd.deleteRegion("Channel 2")
    app.exec_()
