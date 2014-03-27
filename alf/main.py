"""
main.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__copyright__ = ('The CellCognition Project'
                 'Copyright (c) 2006 - 2012'
                 'Gerlich Lab, IMBA Vienna, Austria'
                 'see AUTHORS.txt for contributions')
__licence__ = 'LGPL'
__url__ = 'www.cellcognition.org'

from os.path import splitext

from PyQt4 import uic
from PyQt4 import QtGui
# from PyQt4 import QtCore

from alf.graphicsview import AlfGraphicsView

class AlfMainWindow(QtGui.QMainWindow):

    def __init__(self, file_=None, region=None, *args, **kw):
        super(AlfMainWindow, self).__init__(*args, **kw)

        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowTitle("AlfMainWindow")

        self.tileview = AlfGraphicsView(file_, region, parent=self)
        self.setCentralWidget(self.tileview)
