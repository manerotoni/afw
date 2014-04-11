"""
sorting.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from os.path import splitext
from PyQt4 import uic
from PyQt4 import QtGui


class AfSidebar(QtGui.QToolBox):

    def __init__(self, *args, **kw):
        super(AfSidebar, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
