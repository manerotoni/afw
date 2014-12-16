"""
pyassistant.py

The Qt-Project recommends to use the Qt-Assistant for online documentation.
This is a lightweight reimplemntation of the assistant in python to embed
a help browser into a application bundle (i.e using py2exe or py2app).

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from os.path import join, dirname, isfile

from PyQt4 import QtGui
from PyQt4 import QtHelp
from PyQt4.QtCore import Qt
from PyQt4 import uic

from annot.gui.lineedit import AtLineEdit

class AtHelpBrowser(QtGui.QTextBrowser):

    QTHELP = 'qthelp'
    HTTP = 'http'

    def __init__(self, *args, **kw):
        super(AtHelpBrowser, self).__init__(*args, **kw)
        self.helpengine = None

    def setHelpEngine(self, helpengine):
        self.helpengine = helpengine

    def loadResource(self, type_, url):
        if url.scheme() == self.QTHELP:
            return self.helpengine.fileData(url);
        elif url.scheme() == self.HTTP:
            QtGui.QDesktopServices.openUrl(url)
        else:
            return super(AtHelpBrowser, self).loadResource(type_, url);


class AtAssistant(QtGui.QMainWindow):

    def __init__(self, collections_file, *args, **kw):

        if not isfile(collections_file):
            raise IOError("%s file not found" %(collections_file))

        super(AtAssistant, self).__init__(*args, **kw)
        uic.loadUi(join(dirname(__file__), "assistant.ui"), self)

        self.hengine = QtHelp.QHelpEngine(collections_file)
        self.hengine.setupData()
        self.hengine.searchEngine().reindexDocumentation()

        self.hbrowser = AtHelpBrowser()
        self.hbrowser.setHelpEngine(self.hengine)
        self.setCentralWidget(self.hbrowser)
        self.hengine.contentWidget().linkActivated.connect(
            self.hbrowser.setSource)

        self.queries  = self.hengine.searchEngine().queryWidget()
        self.results = self.hengine.searchEngine().resultWidget()
        self.index = self.hengine.indexWidget()
        self.contents = self.hengine.contentWidget()
        self.tabifyDockWidget(self.contentDock, self.indexDock)
        self.tabifyDockWidget(self.contentDock, self.searchDock)
        self.searchDock.hide()

        # search dock (hidden)
        search = QtGui.QFrame(self)
        vbox = QtGui.QVBoxLayout(search)
        vbox.setContentsMargins(3, 3, 3, 3)
        vbox.addWidget(self.queries)
        vbox.addWidget(self.results)
        self.results.requestShowLink.connect(self.hbrowser.setSource)
        self.index.linkActivated.connect(self.hbrowser.setSource)
        self.queries.search.connect(self.search)

        # index dock
        index = QtGui.QFrame(self)
        filterEdit = AtLineEdit(self)
        vbox = QtGui.QVBoxLayout(index)
        vbox.setContentsMargins(3, 3, 3, 3)
        vbox.addWidget(QtGui.QLabel("Look for:"))
        vbox.addWidget(filterEdit)
        vbox.addWidget(self.index)
        filterEdit.textChanged.connect(self.filter)

        self.searchDock.setWidget(search)
        self.contentDock.setWidget(self.contents)
        self.indexDock.setWidget(index)

    def search(self):
        queries = self.queries.query()
        self.hengine.searchEngine().search(queries)

    def filter(self, txt):
        self.hengine.indexModel().filter(txt)



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    hv = AtAssistant(sys.argv[1])
    hv.show()
    app.exec_()
