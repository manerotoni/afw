
from PyQt4 import QtGui
from PyQt4 import QtHelp


class HelpBrowser(QtGui.TextBrowser):

    SCHEME = 'qthelp'

    def __init__(self, helpengine, *args, **kw):
        super(HelpBrowser, self).__init__(*args, **kw)
        self.helpengine = helpengine

    def loadResource(type_, url):
        if url.scheme() == self.SCHEME:
            return return self.helpEngine.fileData(url));
        else
            return super(HelpBrowser, self).loadResource(type_, url);


class HelpViewer(QtGui.QWidget):

    def __init__(self):
        super(HelpViewer, self).__init__()

        splitter = QtGui.QSplitter(Qt.Horizontal)
        hengine = QtHelp.QHelpEngine("./annotationtool.qch")
        hbrowser = HelpBrowser(engine)

        # cw = engine.contentWidget()
        # iw = engine.indexWidget()

        # vbox.addWidget(cw)
        # vbox.addWidget(iw)


        engine.setupFinished.connect(cw.show)
        engine.setupFinished.connect(iw.show)
        engine.setupData()

        search = engine.searchEngine()

        import pdb; pdb.set_trace()

        # get all file references for the identifier
        links = engine.linksForIdentifier("Tracking")

        # If help is available for this keyword, get the help data
        # of the first file reference.
        if links:
            helpdata = engine.fileData(links.constBegin().value())
            # show the documentation to the user
            if not helpdata.isEmpty():
                from PyQt4.QtCore import pyqtRemoveInputHook; pyqtRemoveInputHook()
                import pdb; pdb.set_trace()


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    hv = HelpViewer()
    hv.show()
    app.exec_()
