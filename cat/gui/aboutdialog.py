"""
aboutdialog.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtAboutDialog', )

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from cat import version

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


class AtAboutDialog(QtWidgets.QDialog):

    def __init__(self, *args, **kw):
        super(AtAboutDialog, self).__init__(*args, **kw)
        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setStyleSheet(stylesheet)
        self.setWindowTitle('About AnnotationTool')
        self.setFixedSize(300, 200)

        label1 = QtWidgets.QLabel(self)
        label1.setAlignment(Qt.AlignCenter)
        label1.setText('AnnotationTool\nVersion %s\n\n'
                       'Copyright 2014 Rudolf Hoefler.\nAll rights reserved.\n'
                       %version.version)

        label1.setGeometry(0, 100, 300, 80)
