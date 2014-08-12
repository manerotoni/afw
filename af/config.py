"""
config.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from af.pattern import Singleton

class AfConfig(object):
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
        self.compression_opts = 9

        # uses complemenatary color to draw conturs to improve contrast
        self.contours_complementary_color = True
