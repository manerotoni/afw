"""
prefdialog.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import splitext

from PyQt5 import uic
from PyQt5 import QtWidgets

from cat.config import AtConfig


class AtPreferencesDialog(QtWidgets.QDialog):

    def __init__(self, *args, **kw):
        super(AtPreferencesDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle("Preferences")
        self._compopts_old = dict()

        self.loadSettings()

        self.accepted.connect(self.saveSettings)

        self.hdf_compression.currentIndexChanged[str].connect(
            self.updateCompressionOptions)
        self.hdf_compopts.currentIndexChanged[str].connect(
            self.compoptsUpdated)

    def loadSettings(self):
        # singleton
        atc = AtConfig()

        self.complementary_colors.setChecked(atc.contours_complementary_color)

        self.sort_algorithm.clear()
        self.sort_algorithm.addItems(atc.Sorters)
        self.sort_algorithm.setCurrentIndex(
            self.sort_algorithm.findText(atc.default_sorter))

        self.feature_grouping.clear()
        self.feature_grouping.addItems(atc.FeatureGroups.keys())
        self.feature_grouping.setCurrentIndex(
            self.feature_grouping.findText(atc.default_feature_group))

        self.max_frac_outliers.setValue(atc.max_sv_fraction)

        self.interactive_item_limit.setValue(
            atc.interactive_item_limit)

        self.hdf_compression.clear()
        self.hdf_compression.addItems(atc.Compression.keys())
        self.hdf_compression.setCurrentIndex(
            self.hdf_compression.findText(atc.compression))
        self.updateCompressionOptions(self.hdf_compression.currentText())

        self.hdf_compopts.setCurrentIndex(
            self.hdf_compopts.findText(str(atc.compression_opts)))

    def compoptsUpdated(self, option):
        self._compopts_old[self.hdf_compression.currentText()] = option

    def updateCompressionOptions(self, compression):
        old_state = self.hdf_compopts.blockSignals(True)
        self.hdf_compopts.clear()
        opts = AtConfig.Compression[compression]
        if opts is None:
            self.hdf_compopts.setEnabled(False)
            self.hdf_compopts.addItem("None", None)
        else:
            self.hdf_compopts.setEnabled(True)
            for o in opts:
                self.hdf_compopts.addItem(str(o), o)

        self.hdf_compopts.blockSignals(old_state)
        try:
            idx = self.hdf_compopts.findText(self._compopts_old[compression])
        except KeyError:
            pass
        else:
            if idx > 0:
                self.hdf_compopts.setCurrentIndex(idx)

    def currentCompOpts(self):
        return self.hdf_compopts.itemData(self.hdf_compopts.currentIndex())

    def saveSettings(self):

        atc = AtConfig()

        atc.contours_complementary_color = self.complementary_colors.isChecked()
        atc.default_sorter = self.sort_algorithm.currentText()
        atc.default_feature_group = self.feature_grouping.currentText()

        atc.max_sv_fraction = self.max_frac_outliers.value()
        atc.interactive_item_limit = self.interactive_item_limit.value()
        atc.compression = self.hdf_compression.currentText()
        atc.compression_opts = self.hdf_compopts.itemData(
            self.hdf_compopts.currentIndex()).toPyObject()
