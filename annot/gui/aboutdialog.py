"""
aboutdialog.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtAboutDialog', )

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from annot import version

stylesheet = \
"""
QDialog {
  background: #ffffff;
  background-image: url(:annotationtool_about.png);
}

QLabel {
  font: bold 11px;
  color: white;
}
"""


class AtAboutDialog(QtGui.QDialog):

    def __init__(self, *args, **kw):
        super(AtAboutDialog, self).__init__(*args, **kw)
        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setStyleSheet(stylesheet)
        self.setWindowTitle('About AnnotationTool')
        self.setFixedSize(300, 200)

        label1 = QtGui.QLabel(self)
        label1.setAlignment(Qt.AlignCenter)
        label1.setText('AnnotationTool\nVersion %s\n\n'
                       'Copyright 2014 Rudolf Hoefler. All rights reserved.\n'
                       %version.version)

        label1.setGeometry(0, 100, 300, 70)