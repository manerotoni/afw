"""
setup.py

Usage:
   python setup.py --help

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import join
from distutils.core import setup

import build_helpers

pyrcc_opts = {'infile': join('qrc', 'at_rc.qrc'),
              'outfile': join('af', 'at_rc.py'),
              'pyrccbin': 'pyrcc4'}

setup(name='AnnotationTool',
      version='0.1',
      description='Gallery image based tool for easy class anntotation.',
      author='Rudolf Hoefler',
      author_email='rudolf.hoefler@gmail.com',
      packages = build_helpers.find_submodules("./af", "af"),
      package_data = {'af': ['gui/*.ui', 'gui/sidebar/*.ui']},
      scripts = ['AnnotationTool.py'],
      cmdclass = {'pyrcc': build_helpers.PyRcc,
                  'build': build_helpers.Build},
      options = {'pyrcc': pyrcc_opts, })
