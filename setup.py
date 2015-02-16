"""
setup.py

Usage:
   python setup.py --help

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import glob
from os.path import join
from setuptools import setup
# from distutils.core import setup

from cat import version
import build_helpers

pyrcc_opts = {'infile': join('qrc', 'at_rc.qrc'),
              'outfile': join('cat', 'at_rc.py'),
              'pyrccbin': 'pyrcc4'}

setup(name='AnnotationTool',
      version=version.version,
      description=('Interactive Tool for fast and intuitive'
                   ' classifier training'),
      author='Rudolf Hoefler',
      author_email='rudolf.hoefler@gmail.com',
      packages = build_helpers.find_submodules("./cat", "cat"),
      data_files=[(join('share','AnnotationTool'), glob.glob('./qrc/*.ico'))],
      package_data = {'cat': ['gui/*.ui', 'gui/sidebar/*.ui']},
      scripts = ['AnnotationTool.py', 'postinstall.py'],
      cmdclass = {'pyrcc': build_helpers.PyRcc,
                  'build': build_helpers.Build},
      options = {'pyrcc': pyrcc_opts,
                 'bdist_wininst':
                     {'install_script': 'postinstall.py'}})
