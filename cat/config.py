"""
config.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtConfig", )

from PyQt5.QtCore import QSettings

from cat import version
from cat.pattern import Singleton
from cat.sorters import Sorter
from cat.features import FeatureGroups

class AtConfig(object):
    """Global settings (currently) not visible to the user."""

    __metaclass__ = Singleton

    Compression = {"gzip": range(10),
                   "lzf": None,
                   "None": None}

    FeatureGroups = FeatureGroups
    Sorters = Sorter.sorters()

    def __init__(self):
        # renders contuours in pixmap rather than QGraphicsView
        # if False can cause a segfault in certain cases
        self.draw_contours_in_pixmap = False
        # one of ("gzip", "szip", "lwz", None)
        # szip is not available on every platform
        self.compression = "gzip"
        # 0-9 if gzip else None

        if self.compression  is None:
            self.compression_opts = None
        else:
            self.compression_opts = 4

        # uses complemenatary color to draw conturs to improve contrast
        self.contours_complementary_color = True

        # maximum fraction of support vectors for the one class svm
        # classifier
        self.max_sv_fraction = 0.20

        # if hdf contains more items, than the loading strategy changeds to
        # "interactive", otherwise all item are loaded at oncec
        self.interactive_item_limit = 5000

        self.default_sorter = Sorter.CosineSimilarity
        self.default_feature_group = self.FeatureGroups.keys()[0]

        # include raw image data into the hdf file
        self.save_raw_images = False

    def saveSettings(self):

        settings = QSettings(version.organisation, version.appname)
        settings.beginGroup('Preferences')
        settings.setValue('compression', self.compression)
        settings.setValue('compression_opts', self.compression_opts)
        settings.setValue('max_sv_fraction', self.max_sv_fraction)
        settings.setValue('interactive_item_limit', self.interactive_item_limit)
        settings.setValue('default_sorter', self.default_sorter)
        settings.setValue('default_feature_group', self.default_feature_group)
        settings.setValue('contours_complementary_color',
                          self.contours_complementary_color)
        settings.setValue('save_raw_images', self.save_raw_images)
        settings.endGroup()

    def restoreSettings(self):

        settings = QSettings(version.organisation, version.appname)
        settings.beginGroup('Preferences')

        if settings.contains('compression'):
            value = settings.value('compression', None)
            self.compression = value

        if settings.contains('compression_opts'):
            value = settings.value('compression_opts', None)
            if isinstance(value, basestring):
                self.compression_opts = eval(value)
            else:
                self.compression_opts = value

        if settings.contains('max_sv_fraction'):
            value = settings.value('max_sv_fraction', type=float)
            self.max_sv_fraction = value

        if settings.contains('interactive_item_limit'):
            value = settings.value('interactive_item_limit', 5000, type=int)
            self.interactive_item_limit = value

        if settings.contains('default_sorter'):
            value = settings.value('default_sorter', type=str)
            self.default_sorter = value

        if settings.contains('default_feature_group'):
            value = settings.value('default_feature_group')
            self.default_feature_group = value

        if settings.contains('contours_complementary_color'):
            value = settings.value('contours_complementary_color', type=bool)
            self.contours_complementary_color = value

        if settings.contains('save_raw_images'):
            value = settings.value('save_raw_images', type=bool)
            self.save_raw_images = value

        settings.endGroup()
