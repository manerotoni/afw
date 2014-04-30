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

import build_helpers

pyrcc_opts = {'infile': join('qresources', 'af_rc.qrc'),
              'outfile': join('af', 'af_rc.py'),
              'pyrccbin': 'pyrcc4'}

setup(name='AnnotationFramework',
      version='0.1',
      description='Annotation framework for Micronaut',
      author='Rudolf Hoefler',
      author_email='rudolf.hoefler@gmail.com',
      data_files=[(join('share','micronaut'), glob.glob('./qresources/*.ico'))],
      packages = ['af', 'af.gui'],
      scripts = ['assistant.py'],
      cmdclass = {'pyrcc': build_helpers.PyRcc,
                  'build': build_helpers.Build},
      options = {'pyrcc': pyrcc_opts, })
