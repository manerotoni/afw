"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

import sys
import argparse

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4 import QtGui
from alf.main import AlfMainWindow


if __name__ == '__main__':

    parser = argparse.ArgumentParser(\
        description='Test script for tiled graphicview widget')
    parser.add_argument('file', help='hdf file to load')
    parser.add_argument('--region', help="segmentation region",
                        default="primary__primary")

    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    mw = AlfMainWindow(args.file, args.region)
    mw.show()
    sys.exit(app.exec_())
