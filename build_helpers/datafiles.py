"""
datafiles.py - collect resources for distutils setup
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


__all__ = ['get_data_files', 'find_uifiles',
           'INCLUDES', 'EXCLUDES',]

import os
import glob
import matplotlib
from os.path import join

# for py2app and py2exe
INCLUDES = [ 'sip',
             'h5py.*',
             'scipy.sparse.csgraph._validation',
             'scipy.spatial.kdtree',
             'scipy.sparse.csgraph._shortest_path',
             'scipy.special._ufuncs',
             'scipy.special._ufuncs_cxx',
             'sklearn.utils.sparsetools._graph_validation',
             'cellh5',
             'ontospy',
             'rdflib',
             'rdflib.plugins.memory',
             'rdflib.plugins.parsers.rdfxml',
             'sklearn.utils.lgamma',
             'sklearn.neighbors.typedefs',
             'sklearn.utils.weight_vector' ]

EXCLUDES = ['PyQt5.QtDesigner', 'PyQt5.QtNetwork',
            'PyQt5.QtOpenGL', 'PyQt5.QtScript',
            'PyQt5.QtTest', 'PyQt5.QtWebKit', 'PyQt5.QtXml', 'PyQt5.phonon',
            'PyQt4.QtCore', 'PyQt4.QtGui',  'PyQt4.QtSvg', 'PyQt4',
            '_gtkagg', '_cairo', '_gtkcairo', '_fltkagg',
            '_tkagg',
            'Tkinter',
            'zmq',
            'wx']

def find_uifiles(package_dir):
    uifiles = list()
    for root, dirs, files in os.walk(package_dir):
        for file_ in files:
            if file_.endswith('.ui'):
                uifiles.append(join(root, file_))

    return ("ui", uifiles)


def get_data_files(source_dir):
    """Pack data files into list of (target-dir, list-of-files)-tuples"""

    dfiles = []

    dfiles.extend(matplotlib.get_py2exe_datafiles())

    # qt help files
    dfiles.append(('doc',
                  glob.glob(join("cat", "gui", "helpbrowser", "*.qhc"))))
    dfiles.append(('doc',
                  glob.glob(join("cat", "gui", "helpbrowser", "*.qch"))))

    return dfiles
