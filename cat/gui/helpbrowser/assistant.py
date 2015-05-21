"""
assistant.py

The Qt-Project recommends to use the Qt-Assistant for online documentation.
This is a lightweight reimplemntation of the assistant in python to embed
a help browser into a application bundle (i.e using py2exe or py2app).

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtAssistant", )


from os.path import join, dirname, isfile

from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtHelp
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtGui import QTextDocument

from cat import version
from cat.gui.lineedit import AtLineEdit


class AtHelpBrowser(QtWidgets.QTextBrowser):

    QTHELP = 'qthelp'
    HTTP = 'http'

    def __init__(self, *args, **kw):
        super(AtHelpBrowser, self).__init__(*args, **kw)
        self.helpengine = None

    def setSource(self, url):

        if url.scheme() == self.HTTP:
            QtGui.QDesktopServices.openUrl(url)
        else:
            super(AtHelpBrowser, self).setSource(url)

    def setHelpEngine(self, helpengine):
        self.helpengine = helpengine

    def loadResource(self, type_, url):

        if url.scheme() == self.QTHELP:
            return self.helpengine.fileData(url);
        else:
            return super(AtHelpBrowser, self).loadResource(type_, url);

    def close(self):
        # prevents a segfault on c++ side
        self.helpengine = None


class AtAssistant(QtWidgets.QMainWindow):

    def __init__(self, collections_file, *args, **kw):

        if not isfile(collections_file):
            raise IOError("%s file not found" %(collections_file))

        super(AtAssistant, self).__init__(*args, **kw)
        uic.loadUi(join(dirname(__file__), "assistant.ui"), self)

        self.hengine = QtHelp.QHelpEngine(collections_file)
        self.hengine.setupData()
        self._doc = qchfile = join(dirname(__file__), 'annotationtool.qch')
        self.hengine.registerDocumentation(qchfile)

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
        search = QtWidgets.QFrame(self)
        vbox = QtWidgets.QVBoxLayout(search)
        vbox.setContentsMargins(3, 3, 3, 3)
        vbox.addWidget(self.queries)
        vbox.addWidget(self.results)
        self.results.requestShowLink.connect(self.hbrowser.setSource)
        self.index.linkActivated.connect(self.hbrowser.setSource)
        self.queries.search.connect(self.search)

        # index dock
        index = QtWidgets.QFrame(self)
        filterEdit = AtLineEdit(self)
        vbox = QtWidgets.QVBoxLayout(index)
        vbox.setContentsMargins(3, 3, 3, 3)
        vbox.addWidget(QtWidgets.QLabel("Look for:"))
        vbox.addWidget(filterEdit)
        vbox.addWidget(self.index)
        filterEdit.textChanged.connect(self.filter)

        self.searchDock.setWidget(search)
        self.contentDock.setWidget(self.contents)
        self.indexDock.setWidget(index)

        self._restoreSettings()
        self.indexDock.show()
        self.contentDock.show()

    def waitForIndex(self):
        for i in xrange(50):
            self.thread().msleep(100)
            if not self.hengine.indexModel().isCreatingIndex():
                break

    def openKeyword(self, keyword):
        self.waitForIndex()
        links = self.hengine.indexModel().linksForKeyword(keyword)
        self.hbrowser.setSource(links.values()[0])

    def closeEvent(self, event):
        self._saveSettings()

    def search(self):
        queries = self.queries.query()
        self.hengine.searchEngine().search(queries)

    def filter(self, txt):
        self.hengine.indexModel().filter(txt)

    def _saveSettings(self):
        settings = QtCore.QSettings(version.organisation, version.appname)
        settings.beginGroup('HelpBrowser')
        settings.setValue('state', self.saveState())
        settings.setValue('geometry', self.saveGeometry())
        settings.endGroup()

    def _restoreSettings(self):
        settings = QtCore.QSettings(version.organisation, version.appname)
        settings.beginGroup('HelpBrowser')

        if settings.contains('geometry'):
            geometry = settings.value('geometry')
            self.restoreGeometry(geometry)

        if settings.contains('state'):
            state = settings.value('state')
            self.restoreState(state)

        settings.endGroup()

    def close(self):
        self.hbrowser.close()
        del self.hengine



if __name__ == "__main__":
    import sys
    import cat.cat_rc
    app = QtWidgets.QApplication(sys.argv)
    hv = AtAssistant(sys.argv[1])
    hv.show()
    app.exec_()