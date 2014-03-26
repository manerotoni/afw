"""
tileview.py
"""

__author__ = 'rudolf.hoefler@gmail.com'

import sys
import argparse
from PyQt4 import QtGui
from tileview import GraphicsTileView


if __name__ == '__main__':

    parser = argparse.ArgumentParser(\
        description='Test script for tiled graphicview widget')
    parser.add_argument('file', help='hdf file to load')
    parser.add_argument('--region', help="segmentation region",
                        default="primary__primary")

    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    tileview = GraphicsTileView(args.file, args.region)
    tileview.show()
    sys.exit(app.exec_())
