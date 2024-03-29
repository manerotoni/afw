"""
build_helpers.py

Functions and classes for the build process.

"""


__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'LGPL'

__all__ = ('Build', 'BuildRcc', 'BuildHelp')


from os.path import isfile
import subprocess
from  distutils.core import Command
from  distutils.command.build import build as _build


class Build(_build):
    """Custom build command for distutils to have the qrc files compiled before
    before the build process.
    """

    def run(self):
        self.run_command('build_rcc')
        self.run_command('build_help')
        _build.run(self)


class BuildHelp(Command):
    """Custom command to compile Qt Collection files"""

    description = "Compile qt4-collection files"
    user_options = [('qcollectiongeneator=', 'b', 'Path to qcollectiongeneator'),
                    ('infile=', 'i', 'Input file'),
                    ('outfile=', 'o', 'Output file')]

    def initialize_options(self):
        self.qcollectiongeneator = 'qcollectiongeneator'
        self.infile = None
        self.outfile = None

    def finalize_options(self):

        if not isfile(self.infile):
            raise RuntimeError('file %s not found' %self.infile)

        if not self.outfile.endswith('.qhc'):
            raise RuntimeError("Check extension of the output file")

    def run(self):
        print "Compiling colleciton file"
        print self.outfile
        try:
            subprocess.check_call([self.qcollectiongeneator, '-o', self.outfile,
                                   self.infile])
        except Exception, e:
            cmd = "%s -o %s %s" %(self.qcollectiongeneator,
                                  self.outfile, self.infile)
            print "running command '%s' failed" %cmd
            raise


class BuildRcc(Command):
    """Custom command to compile Qt4-qrc files"""

    description = "Compile qt4-qrc files"
    user_options = [('pyrccbin=', 'b', 'Path to pyrcc4 executable'),
                    ('infile=', 'i', 'Input file'),
                    ('outfile=', 'o', 'Output file')]

    def initialize_options(self):
        self.pyrccbin = 'pyrcc4'
        self.infile = None
        self.outfile = None

    def finalize_options(self):
        if not isfile(self.infile):
            raise RuntimeError('file %s not found' %self.infile)

        if not self.outfile.endswith('.py'):
            raise RuntimeError("Check extension of the output file")

    def run(self):
        print "Compiling qrc file"
        print self.outfile
        try:
            subprocess.check_call([self.pyrccbin, '-o', self.outfile,
                                   self.infile])
        except Exception, e:
            cmd = "%s -o %s %s" %(self.pyrccbin, self.outfile, self.infile)
            print "running command '%s' failed" %cmd
            raise
