# -*- mode: python -*-

block_cipher = None

import os

import matplotlib
matplotlib.rcsetup.all_backends = ["Qt5Agg"]

from cat import version

def find_files(search_dir, extension):

    uifiles = list()
    for root, dirs, files in os.walk(search_dir):
        for file_ in files:
            if file_.endswith(extension):
                ff = os.path.join(root, file_)
                uifiles.append((ff, os.path.abspath(ff), "DATA"))
    return uifiles


a = Analysis(['CellAnnotator.py'],
             pathex=['z:\\workbench\\afw'],
             hiddenimports=['sklearn.utils.sparsetools._graph_validation',
                            'sklearn.utils.sparsetools._graph_tools',
                            'sklearn.utils.lgamma',
                            'sklearn.utils.weight_vector',
                            'cat.gui.imagewidget',
                            'cat.gui.slider'],
             hookspath=None,
             runtime_hooks=None,
             excludes=['zmq.backends', 'IPython', 'zmq', 'sip', 'PyQt4', 'PIL'
                       'PIL.SpiderImagePlugin'],

             cipher=block_cipher)

files = find_files('cat', '.ui')
files += find_files('cat', '.qhc')
files += find_files('cat', '.qch')
a.datas += files

# workarround for custom installation of sip and pyqt5
for binary in a.binaries:
    if 'sip' in binary[0]:
        a.binaries.append(('sip.pyd', binary[1], binary[2]))
        break

pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='%s.exe' %version.appstr,
          debug=False,
          strip=None,
          upx=True,
          console=False , icon='qrc\\annotationtool.ico')
