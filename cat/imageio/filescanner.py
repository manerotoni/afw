"""
filescanner.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import os
import glob
from os.path import isdir, join

from PyQt5 import QtGui

from collections import OrderedDict
from cat.pattern import Factory

class FileScanner(object):

    __metaclass__ = Factory

    def __init__(self, imagedir, *args, **kw):
        super(FileScanner, self).__init__(*args, **kw)
        self.imagedir = imagedir

    @classmethod
    def scanners(self):
        return [c.__name__ for c in sorted(self._classes.values())]

    def __cmp__(self, other):
        return self._key < other._key

    @staticmethod
    def icon():
        raise NotImplementedError

    @classmethod
    def iterclasses(self):
        for n, c in self._classes.iteritems():
            yield n, c

class FlatDirectory(FileScanner):
    """Scann a flat directory for image files (tif and lsm).
    Files are not tagged with a treament."""

    _key = 1

    def __init__(self, *args, **kw):
        super(FlatDirectory, self).__init__(*args, **kw)

    def __call__(self):
        pattern1 = self.imagedir + "/*.lsm"
        pattern2 = self.imagedir + "/*.tif"
        files = glob.glob(pattern1) + glob.glob(pattern2)

        tfiles = OrderedDict()
        for f in files:
            tfiles[f] = None
        return tfiles

    @staticmethod
    def icon():
        return QtGui.QIcon(':/flat_directory01.png')


class DirectoryPerTreatment(FileScanner):
    """Scann a directory for subdirectories and each subdirectories
    for image files (tif and lsm).
    Files are tagged with the subdirectry name as treatment.
    """

    _key = 2

    def __init__(self, *args,**kw):
        super(DirectoryPerTreatment, self).__init__(*args, **kw)

    def __call__(self):

        tfiles = OrderedDict()

        for item in os.listdir(self.imagedir):
            root = join(self.imagedir, item)

            if isdir(root):
                pattern1 = join(root, "*.lsm")
                pattern2 = join(root, "*.tif")
                files = glob.glob(pattern1) + glob.glob(pattern2)

                for f in files:
                    tfiles[f] = item

        return tfiles

    @staticmethod
    def icon():
        return QtGui.QIcon(':/directory_per_treatment.png')
