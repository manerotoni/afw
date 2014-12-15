
from PyQt4 import QtGui
from PyQt4 import QtHelp
from PyQt4.QtCore import Qt


class HelpBrowser(QtGui.QTextBrowser):

    SCHEME = 'qthelp'

    def __init__(self, helpengine, *args, **kw):
        super(HelpBrowser, self).__init__(*args, **kw)
        self.helpengine = helpengine

    def loadResource(self, type_, url):
        if url.scheme() == self.SCHEME:
            return self.helpengine.fileData(url);
        else:
            return super(HelpBrowser, self).loadResource(type_, url);


class HelpViewer(QtGui.QWidget):

    def __init__(self):
        super(HelpViewer, self).__init__()

        splitter = QtGui.QSplitter(Qt.Horizontal, self)
        splitter.setStretchFactor(1, 1)
        hengine = QtHelp.QHelpEngine("./annotationtool.qhc")
        hengine.setupData()

        hbrowser = HelpBrowser(hengine)

        hengine.contentWidget().linkActivated.connect(
        hbrowser.setSource)

        splitter.insertWidget(0, hengine.contentWidget())
        splitter.insertWidget(1, hbrowser)


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    hv = HelpViewer()
    hv.show()
    app.exec_()
