#!/usr/bin/env Python

"""
CellAnnotator.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import os
from os.path import dirname, join
import sys
import argparse

# special case on windoze
try:
    import PyQt5.sip as sip
except ImportError:
    import sip

sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from matplotlib import use
use("Qt5Agg")

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from cat.gui.main import AtMainWindow
from cat import version


if __name__ == '__main__':
    parser = argparse.ArgumentParser(\
        description='Test script for tiled graphicview widget')
    parser.add_argument('--file', '-f', help='hdf file to load', default=None)
    args = parser.parse_args()

    if args.file is not None and not os.path.isfile(args.file):
        raise SystemExit("File does not exist!")

    app = QApplication(sys.argv)

    # windows always sucks!!
    if sys.platform.startswith("win"):
        sqldrivers = join(dirname(QtGui.__file__), "plugins")
        app.addLibraryPath(sqldrivers)


    splash_pix = QPixmap(':annotationtool_about.png')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    splash.showMessage(version.information,
                       alignment=Qt.AnchorHorizontalCenter|
                       Qt.AnchorVerticalCenter)
    app.processEvents()
    mw = AtMainWindow(args.file)
    mw.show()
    app.thread().msleep(1000)
    splash.finish(mw)

    sys.exit(app.exec_())
