"""
config.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtConfig", )

from annot.pattern import Singleton
from annot.sorters import Sorter

class AtConfig(object):
    """Global settings (currently) not visible to the user."""

    __metaclass__ = Singleton

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