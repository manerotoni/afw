
from PyQt4 import QtGui
from PyQt4 import QtHelp


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    engine = QtHelp.QHelpEngine("./annotationtool.qch")

    widget = engine.contentWidget()
    # widget.show()

    iw = engine.indexWidget()
    # iw.show()


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

    app.exec_()
