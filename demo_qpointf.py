
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

    point = QtCore.pyqtSignal(list)

    def run(self):

        for i in xrange(1000):
            for i in xrange(0, 400, 5):
                polygons = list()
                for j in xrange(0, 400, 5):
                    polygons.append([(i, j), (i, j+5), (i+5, j+5)])
                self.msleep(10)
                self.point.emit(polygons)


class GraphicsView(QtGui.QGraphicsView):

    def __init__(self, *args, **kw):
        super(GraphicsView, self).__init__(*args, **kw)
        self.setScene(QtGui.QGraphicsScene())
        self.resize(500, 500)

    @property
    def scalefactor(self):
        return self.transform().m11()

    def scale(self, sx, sy):
        if sx*self.scalefactor:
            super(GraphicsView, self).scale(sx, sy)

    def wheelEvent(self, event):

        if event.modifiers() == Qt.ControlModifier:

            if event.delta() > 0:
                factor = 1.1
            else:
                factor = 0.9
            self.scale(factor, factor)

    def clearPolygons(self):
        for item in self.scene().items():
            if isinstance(item, QtGui.QGraphicsPolygonItem):
                self.scene().removeItem(item)

    def addPolygons(self, polygons):
        self.clearPolygons()
        for polygon in polygons:
            qpolygon = QtGui.QPolygonF([QtCore.QPointF(*pt) for pt in polygon])
            self.scene().addPolygon(qpolygon)


class Window(QtGui.QWidget):

    def __init__(self, *args, **kw):
        super(Window, self).__init__(*args, **kw)
        self.resize(600, 600)
        vbox = QtGui.QVBoxLayout(self)
        closeBtn = QtGui.QPushButton("close")
        closeBtn.clicked.connect(self.close)
        self.label = QtGui.QLabel("foobar")
        self.view = GraphicsView(self)
        vbox.addWidget(self.view)
        vbox.addWidget(closeBtn)

        self.thread = Thread()
        self.thread.start()
        self.thread.point.connect(self.view.addPolygons, Qt.QueuedConnection)


app = QtGui.QApplication(sys.argv)

cw = Window()
cw.show()

app.exec_()


# for i in xrange(10000000000):
#     qp =  QtCore.QPointF(i, i)
#     print QtCore.QThread.currentThreadId(), qp
