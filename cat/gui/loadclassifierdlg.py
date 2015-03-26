"""
loadclassiferdlg.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("LoadClassifierDialog", )

import h5py

from os.path import splitext, expanduser
from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog


class LoadClassifierDialog(QtGui.QDialog):

    def __init__(self, *args, **kw):
        super(LoadClassifierDialog, self).__init__(*args, **kw)
        uifile = splitext(__file__)[0] + ".ui"
        uic.loadUi(uifile, self)

        self.descriptions = dict()

        self.pathBtn.clicked.connect(self.onPathBtn)
        self.classifier_name.currentIndexChanged[str].connect(
            self.onClassifierChanged)

    def onClassifierChanged(self, name):

        try:
            self._description.clear()
            txt = self.descriptions[name]
        except KeyError:
            pass
        else:
            self._description.appendPlainText(txt)

    def onPathBtn(self):

        file_ = QFileDialog.getOpenFileName( \
            self, "Select a config file", expanduser('~'),
            ("hdf5 files (*.ch5 *.hdf5 *.h5 *.he5 *.hdf *.hdf4 *.he2 *.he5;;"
            ";;All files (*.*)"))

        if file_:
            self._path.setText(file_)
            self.path = file_

            try:
                fp = h5py.File(file_, "r")
                clf_names = fp['classifiers'].keys()
            except KeyError as e:
                QtGui.QMessageBox.critical(self, "Error", "No classifiers found")
                raise KeyError("No classfiers found")

            else:
                self.classifier_name.clear()
                self.classifier_name.addItems(clf_names)
                self.descriptions.clear()
                for name in clf_names:
                    try:
                        desc = fp['classifiers/%s' %name].attrs["description"]
                        self.descriptions[name] = desc
                    except KeyError:
                        pass
            finally:
                fp.close()
