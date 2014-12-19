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

from annot import version
import build_helpers

pyrcc_opts = {'infile': join('qrc', 'at_rc.qrc'),
              'outfile': join('annot', 'at_rc.py'),
              'pyrccbin': 'pyrcc4'}

setup(name='AnnotationTool',
      version=version.version,
      description='Gallery image based tool for easy class anntotation.',
      author='Rudolf Hoefler',
      author_email='rudolf.hoefler@gmail.com',
      packages = build_helpers.find_submodules("./annot", "annot"),
      data_files=[(join('share','AnnotationTool'), glob.glob('./qrc/*.ico'))],
      package_data = {'annot': ['gui/*.ui', 'gui/sidebar/*.ui']},
      scripts = ['AnnotationTool.py', 'postinstall.py'],
      cmdclass = {'pyrcc': build_helpers.PyRcc,
                  'build': build_helpers.Build},
      options = {'pyrcc': pyrcc_opts,
                 'bdist_wininst':
                     {'install_script': 'postinstall.py'}})
