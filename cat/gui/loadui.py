"""
loadUI.py

Search for qt ui files in two different locations.

1) beside the python module
2) <workingdir>/ui

The second option is a special case for bundel osx binary distribution

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from os.path import basename, isfile, join

from PyQt5 import uic

def loadUI(filename, widget):
    if isfile(filename):
        return uic.loadUi (filename, widget)
    else:
        return uic.loadUi(
            join("ui", basename(filename)), widget)
