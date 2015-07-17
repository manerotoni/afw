"""
setup_mac.py

Setup script for MacOSX.

Usage:
   python setup_mac.py py2app

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import join
import py2app

from distutils.core import setup
import build_helpers

from cat import version


py2app_opts = {'excludes': build_helpers.EXCLUDES,
               'includes': ['sip',
                            'PyQt5'
                            'PyQt5.Qt'
                            'PyQt5.QtCore',
                            'PyQt5.QtGui',
                            'PyQt5.QtWidgets',
                            'cat.gui.imagewidget',
                            'cat.gui.slider'],
               "qt_plugins": ['platforms', 'sqldrivers'],
               "argv_emulation":False,
               "strip": True,
               "optimize": 1,
               "iconfile": "qrc/annotationtool.icns",
               "packages": ["h5py","vigra","sklearn"],
               "arch": "x86_64",
               "matplotlib_backends": ["qt5agg"]}


pyrcc_opts = {'infile': join('qrc', 'cat_rc.qrc'),
              'outfile': join('cat', 'cat_rc.py'),
              'pyrccbin': 'pyrcc5'}

help_opts = {'infile': join('doc', 'annotationtool.qhcp'),
             'outfile':
             join('cat', 'gui', 'helpbrowser', 'annotationtool.qhc'),
             'qcollectiongeneator': 'qcollectiongenerator'}

# python package to distribute
dfiles = build_helpers.get_data_files("./cat")
# no ui files in package data for py2app
uifiles = build_helpers.find_uifiles('./cat')
dfiles.append(uifiles)

setup(app = ['CellAnnotator.py'],
      #name='CellAnnotator',
      version=version.version,
      description=('Interactive Tool for fast and intuitive'
                   ' classifier training'),
      author='Rudolf Hoefler',
      author_email='rudolf.hoefler@gmail.com',
      packages = build_helpers.find_submodules("./cat", "cat"),

      data_files = dfiles,
      options = {"py2app": py2app_opts,
                 "build_help": help_opts,
                 "build_rcc": pyrcc_opts},
      cmdclass = {'build_rcc': build_helpers.BuildRcc,
                  'build_help': build_helpers.BuildHelp,
                  'build': build_helpers.Build},
      setup_requires=['py2app'])
