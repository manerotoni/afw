
"""
demo_qpoint.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt


class Thread(QtCore.QThread):

    point = QtCore.pyqtSignal(tuple)

    def run(self):

        for i in xrange(1000000):
            print "thread: ", QtCore.QThread.currentThread()
            self.msleep(5)
            self.point.emit(tuple((i, i)))


class CloseWindow(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(CloseWindow, self).__init__(*args, **kw)
        vbox = QtGui.QVBoxLayout(self)
        closeBtn = QtGui.QPushButton("close")
        closeBtn.clicked.connect(self.close)
        vbox.addWidget(closeBtn)
        self.label = QtGui.QLabel("foobar")
        vbox.addWidget(self.label)

        self.thread = Thread()
        self.thread.start()
        self.thread.point.connect(self.setLabel, Qt.QueuedConnection)

    def setLabel(self, vector):
        qp = QtCore.QPointF(*vector)
        print "gui: ", QtCore.QThread.currentThread()
        self.label.setText("%s-%s" %(qp.x(), qp.y()))

app = QtGui.QApplication(sys.argv)

cw = CloseWindow()
cw.show()

app.exec_()


# for i in xrange(10000000000):
#     qp =  QtCore.QPointF(i, i)
#     print QtCore.QThread.currentThreadId(), qp
