"""
savehdfdlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("SaveClassifierDialog", )


from os.path import splitext
from PyQt4 import uic
from PyQt4 import QtGui


class SaveClassifierDialog(QtGui.QDialog):

    def __init__(self, *args, **kw):
        super(SaveClassifierDialog, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        uic.loadUi(uifile, self)

    @property
    def overwrite(self):
        return self._overwrite.isChecked()

    @property
    def name(self):
        return self._name.text()

    @name.setter
    def name(self, name):
        self._name.setText(name)

    @property
    def path(self):
        return self._path.text()

    @path.setter
    def path(self, path):
        self._path.setText(path)

    @property
    def description(self):
        txt = self._description.toPlainText()
        if txt:
            return txt
        else:
            return None
