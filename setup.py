"""
setup.py

Usage:
   python setup.py --help

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import glob
from os.path import join
from distutils.core import setup

from cat import version

pyrcc_opts = {'infile': join('qrc', 'cat_rc.qrc'),
              'outfile': join('cat', 'cat_rc.py'),
              'pyrccbin': join('C:\\', 'Python27', 'Lib', 'site-packages',
                               'PyQt5', 'pyrcc5.exe')}

help_opts = {'infile': join('doc', 'annotationtool.qhcp'),
             'outfile':
             join('cat', 'gui', 'helpbrowser', 'annotationtool.qhc'),
             'qcollectiongeneator': 'qcollectiongenerator'}

setup(name='CellAnnotator',
      version=version.version,
      description=('Interactive Tool for fast and intuitive'
                   ' classifier training'),
      author='Rudolf Hoefler',
      author_email='rudolf.hoefler@gmail.com',
      packages = build_helpers.find_submodules("./cat", "cat"),
      data_files=[(join('share','CellAnnotator'), glob.glob('./qrc/*.ico'))],
      package_data = {'cat': ['gui/*.ui', 'gui/sidebar/*.ui',
                              'gui/helpbrowser/*.ui',
                              'gui/helpbrowser/annotationtool.qhc',
                              'gui/helpbrowser/annotationtool.qch'],},
      scripts = ['CellAnnotator.py', 'postinstall.py'],
      cmdclass = {'pyrcc': build_helpers.PyRcc,
                  'build_help': build_helpers.BuildHelp,
                  'build': build_helpers.Build},
      options = {'pyrcc': pyrcc_opts,
                 'build_help': help_opts,
                 'bdist_wininst':
                     {'install_script': 'postinstall.py'}})
