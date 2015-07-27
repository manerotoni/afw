"""
savehdfdlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("SaveClassifierDialog", )


from os.path import splitext, expanduser

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox

from cat.hdfio.readercore import HdfError
from cat.gui.loadui import loadUI

class SaveClassifierDialog(QtWidgets.QDialog):

    def __init__(self, classifier, labels, sample_info, description,
                 *args, **kw):
        super(SaveClassifierDialog, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        loadUI(uifile, self)

        self._description.setPlainText(description)
        self.classifier = classifier
        self.labels = labels
        self.sinfo = sample_info
        self.name = classifier.name.replace(" ", "_").lower()

        self.pathBtn.clicked.connect(self.onPathBtn)

    def accept(self):
        try:
            self.classifier.saveToHdf(self.name,
                                      self.path,
                                      self.parent().featuredlg.checkedItems(),
                                      self.description,
                                      self.overwrite,
                                      self.labels,
                                      self.sinfo)
        except HdfError as e:
            QMessageBox.critical(self, "error", str(e))
        else:
            QMessageBox.information(self, "information",
                                    "Data saved successfully")

        super(SaveClassifierDialog, self).accept()


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

    def onPathBtn(self):

        file_ = QFileDialog.getSaveFileName(
            self, "Save File as...",
            expanduser("~"),
            "hdf files (*.hdf *.h5 *.hdf5 *.he5 *.ch5)")

        if file_:
            self.path = file_
