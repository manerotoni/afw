"""
segmentationdlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('SegmentationDialog', )

import os
import sys
from collections import OrderedDict
from os.path import splitext, join, dirname

import h5py

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtCore import Qt, pyqtSignal

from af.gui.featurebox import FeatureBox
from af.hdfio.trainingset import AtTrainingSetIO
from af.segmentation import PrimaryParams, ExpansionParams, SRG_TYPE
from af.xmlconf import XmlConfReader, XmlConfWriter

# windows sucks!
try:
    import magic

    def settings_from(filename):
        if magic.from_file(filename, mime=True) == "application/xml":
            with open(filename, "r") as fp:
                return fp.read()
        elif magic.from_file(filename, mime=True) == "application/x-hdf":
            try:
                fp = AtTrainingSetIO(filename)
                return fp.settings
            finally:
                fp.close()
        raise IOError("Unknown extenstion!")

except ImportError:
    def settings_from(filename):
        extenstion = os.path.splitext()[0]
        if extenstion == "xml":
            with open(filename, "r") as fp:
                return fp.read()
        elif extenstion in ("hdf", "ch5", "h5", "hdf5"):
            try:
                fp = AtTrainingSetIO(filename)
                return fp.settings
            finally:
                fp.close()

        raise IOError("Unknown extenstion!")




class ChLabel(QtGui.QLabel):

    def __init__(self, *args, **kw):
        super(ChLabel, self).__init__(*args, **kw)
        self.setAlignment(Qt.AlignHCenter|Qt.AlignRight)


class ExpansionWidget(QtGui.QGroupBox):

    def __init__(self, *args, **kw):
        super(ExpansionWidget, self).__init__(*args, **kw)
        uic.loadUi(join(dirname(__file__), "expansionregion.ui"), self)

    def setValue(self, value):
        self.expansionSize.setValue(value)

    def value(self):
        return self.expansionSize.value()

    def params(self):
        return ExpansionParams(
            SRG_TYPE["KeepContours"], None, 0, self.value(), 0,
            self.normMin.value(),
            self.normMax.value())

    def setParams(self, params):
        self.normMin.setValue(params.norm_min)
        self.normMax.setValue(params.norm_max)
        self.setValue(params.expansion_size)


class SegmentationDialog(QtGui.QWidget):

    _ncols = 3

    # indices for widgetAt method
    NAME = 0
    SEGMENTATION = 1
    FEATURES = 2

    activateChannels = pyqtSignal(list)
    changeColor = pyqtSignal(str, str)

    def __init__(self, *args, **kw):
        super(SegmentationDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowFlags(Qt.Window)
        # row count (rowCount from gridlayout is not reliable!)
        self._rcount = 1

        self.pchannel.currentIndexChanged[str].connect(self.onChannelChanged)
        self.loadBtn.clicked.connect(self.onLoadBtn)
        self.saveBtn.clicked.connect(self.onSaveBtn)

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
        return PrimaryParams(self.medianRadius.value(),
                             self.windowSize.value(),
                             self.minContrast.value(),
                             self.removeBorderObjects.isChecked(),
                             self.fillHoles.isChecked(),
                             self.normMin.value(),
                             self.normMax.value(),
                             self.sizeMin.value(),
                             self.sizeMax.value(),
                             self.intensityMin.value(),
                             self.intensityMax.value(),
                             self.galSize.value())

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

    def onSaveBtn(self):

        dir_ = os.path.expanduser("~")
        fname = QtGui.QFileDialog.getSaveFileName(
            self, "save File", dir_, "xml files (*.xml)")

        active_channels = self.parent().cbar.checkedChannels()
        colors = self.parent().cbar.colors()

        if fname:
            writer = XmlConfWriter(self.segmentationParams(),
                                   self.featureGroups(),
                                   active_channels.values(),
                                   colors)
            writer.save(fname)

    def onLoadBtn(self):
        dir_ = os.path.expanduser("~")
        fname = QtGui.QFileDialog.getOpenFileName(
            self, "load config file", dir_,
            ("xml files (*.xml);;"
             "hdf5 files (*.hdf5 *.h5 *.he5 *.hdf *.hdf4 *.he2 *.he5;;"
             "All files (*.*)"))

        if fname:
            xmldata = settings_from(fname)
            reader = XmlConfReader(xmldata)
            self.activateChannels.emit(reader.activeChannels())
            # primary settings
            name, settings = reader.primarySettings()
            self._updatePrimary(name, settings)
            # reads predifined color for channel
            self.changeColor.emit(name, reader.color(name))

            for i in xrange(1, self._rcount):
                cname = self.widgetAt(i, self.NAME).text()
                try:
                    settings = reader.expandedSettings(cname)
                    self.changeColor.emit(cname, reader.color(cname))
                except ValueError:
                    continue
                self._updateExtendedRegion(i, settings)

    def _updatePrimary(self, name, settings):
        """Update the form for the primary segmentation."""

        idx = self.pchannel.findText(name)
        if idx != -1:
            self.pchannel.setCurrentIndex(idx)

        segpar = settings[XmlConfReader.SEGMENTATION]

        self.minContrast.setValue(segpar.min_contrast)
        self.medianRadius.setValue(segpar.median_radius)
        self.windowSize.setValue(segpar.window_size)
        self.fillHoles.setChecked(segpar.fill_holes)
        self.removeBorderObjects.setChecked(segpar.remove_borderobjects)
        self.normMin.setValue(segpar.norm_min)
        self.normMax.setValue(segpar.norm_max)
        self.sizeMin.setValue(segpar.size_min)
        self.sizeMax.setValue(segpar.size_max)
        self.intensityMin.setValue(segpar.intensity_min)
        self.intensityMax.setValue(segpar.intensity_max)
        self.galSize.setValue(segpar.gallery_size)

        fwidget = self.widgetAt(0, self.FEATURES)
        fwidget.setFeatureGroups(settings[XmlConfReader.FEATUREGROUPS])

    def _updateExtendedRegion(self, index, settings):
        """Update the form for extended segementation region by given by name"""

        ewidget = self.widgetAt(index, self.SEGMENTATION)
        ewidget.setParams(settings[XmlConfReader.SEGMENTATION])

        fwidget = self.widgetAt(index, self.FEATURES)
        fwidget.setFeatureGroups(settings[XmlConfReader.FEATUREGROUPS])


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    sd = SegmentationDialog()
    sd.setRegions(["Channel 1", "Channel 2"])
    sd.show()
    app.exec_()
