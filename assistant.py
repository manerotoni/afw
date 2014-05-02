#!/usr/bin/env Python

"""
assistant.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ ='GPL'

import sys
import argparse

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 1)

from PyQt4 import QtGui
from af.gui import AfMainWindow


if __name__ == '__main__':

    parser = argparse.ArgumentParser(\
        description='Test script for tiled graphicview widget')
    parser.add_argument('--file', '-f', help='hdf file to load', default=None)


    args = parser.parse_args()
    app = QtGui.QApplication(sys.argv)
    mw = AfMainWindow(args.file)
    mw.show()
    sys.exit(app.exec_())
