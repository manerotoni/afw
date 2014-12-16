
from PyQt4 import QtGui
from PyQt4 import QtHelp
from PyQt4.QtCore import Qt
from PyQt4 import uic

class HelpBrowser(QtGui.QTextBrowser):

    QTHELP = 'qthelp'
    HTTP = 'http'

    def __init__(self, *args, **kw):
        super(HelpBrowser, self).__init__(*args, **kw)
        self.helpengine = None

        print 100*'#'

    def setHelpEngine(self, helpengine):
        self.helpengine = helpengine

    def loadResource(self, type_, url):
        if url.scheme() == self.QTHELP:
            return self.helpengine.fileData(url);
        elif url.scheme() == self.HTTP:
            QtGui.QDesktopServices.openUrl(url)
        else:
            return super(HelpBrowser, self).loadResource(type_, url);


class PyAssistant(QtGui.QMainWindow):

    def __init__(self, collections_file, *args, **kw):
        super(PyAssistant, self).__init__(*args, **kw)
        uic.loadUi("pyassistant.ui", self)

        self.hengine = QtHelp.QHelpEngine(collections_file)
        self.hengine.setupData()

        self.hbrowser = HelpBrowser()
        self.hbrowser.setHelpEngine(self.hengine)
        self.setCentralWidget(self.hbrowser)
        self.hengine.contentWidget().linkActivated.connect(
            self.hbrowser.setSource)

        self.queries  = self.hengine.searchEngine().queryWidget()
        self.results = self.hengine.searchEngine().resultWidget()
        self.tabifyDockWidget(self.indexDock, self.contentDock)
        self.tabifyDockWidget(self.contentDock, self.searchDock)

        self.results.requestShowLink.connect(self.hbrowser.setSource)

        self.hengine.searchEngine().reindexDocumentation()

        self.queries.search.connect(self.search)

        self.searchDock.setWidget(self.queries)
        self.contentDock.setWidget(self.hengine.contentWidget())
        self.indexDock.setWidget(self.hengine.indexWidget())

        # hbox.addWidget(self.results)
        # hbox.addWidget(self.hengine.contentWidget())
        # hbox.addWidget(self.hbrowser)

    def search(self):
        queries = self.queries.query()
        self.hengine.searchEngine().search(queries)
        # print self.hengine.searchEngine().query()
        # self.results.search(queries)
        # # print results.hitCount()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    hv = PyAssistant('./annotationtool.qhc')
    hv.show()
    app.exec_()
