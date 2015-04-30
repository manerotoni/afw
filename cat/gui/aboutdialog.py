"""
aboutdialog.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('AtAboutDialog', )

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from cat import version

stylesheet = \
"""
QDialog {
  background: #ffffff;
  background-image: url(:annotationtool_about.png);
}
"""


class AtAboutDialog(QtGui.QDialog):

    def __init__(self, *args, **kw):
        super(AtAboutDialog, self).__init__(*args, **kw)
        self.setBackgroundRole(QtGui.QPalette.Dark)
        self.setStyleSheet(stylesheet)
        self.setWindowTitle('About %s' %version.appname)
        self.setFixedSize(424, 254)

        label = QtGui.QLabel(self)
        label.setStyleSheet(stylesheet)
        label.setAlignment(Qt.AlignCenter)
        label.setText(version.information)
        label.setGeometry(0, 0, 424, 254)
        label.show()
