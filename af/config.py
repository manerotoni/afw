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
