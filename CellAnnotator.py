#!/usr/bin/env Python

"""
CellAnnotator.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ ='GPL'

import os
from os.path import dirname, join
import sys
import argparse

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 1)

from PyQt4 import QtGui
from PyQt4.QtGui import QApplication, QSplashScreen, QPixmap
from PyQt4.QtCore import Qt
from cat.gui.main import AtMainWindow
from cat import version

if __name__ == '__main__':
    parser = argparse.ArgumentParser(\
        description='Test script for tiled graphicview widget')
    parser.add_argument('--file', '-f', help='hdf file to load', default=None)
    args = parser.parse_args()

    if args.file is not None and not os.path.isfile(args.file):
        raise SystemExit("File does not exist!")

    app = QtGui.QApplication(sys.argv)

    # windows always sucks!!
    if sys.platform.startswith("win"):
        sqldrivers = join(dirname(QtGui.__file__), "plugins")
        app.addLibraryPath(sqldrivers)

    mw = AtMainWindow(args.file)

    splash_pix = QPixmap(':annotationtool_about.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage(version.information,
                       alignment=Qt.AnchorHorizontalCenter|
                       Qt.AnchorVerticalCenter)
    app.processEvents()
    mw.show()
    app.thread().msleep(1500)
    splash.finish(mw)

    sys.exit(app.exec_())
