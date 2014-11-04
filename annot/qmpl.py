"""
qmpl.py

code copied from https://github.com/rhoef/mpl-qtdemo

"""

__author__ = 'rudolf.hoefler@gmail.com'
__copyright__ = 'LGPL'

__all__ = ('QNavigationToolbar', 'QFigureWidget', 'QFigureTabWidget')


from matplotlib import rcParams
from matplotlib.colors import rgb2hex
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT

from PyQt4 import QtGui
from PyQt4 import QtCore


class QNavigationToolbar(NavigationToolbar2QT):
    """Custom toolbar that does not insert a newline in the status message."""

    message = QtCore.Signal(str)

    def __init__(self, *args, **kw):
        super(QNavigationToolbar, self).__init__(*args, **kw)

    def toggle(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()

    def set_message(self, s):
        self.message.emit(s)
        if self.coordinates:
            self.locLabel.setText(s)


class QFigureWidget(QtGui.QWidget):
    """Widget to layout the actual figure and toolbar. Further it forwards.
    the key press events from the widget to the figure."""

    def __init__(self, fig, *args, **kw):
        super(QFigureWidget, self).__init__(*args, **kw)
        self.fig = fig

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setParent(self)
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()

        color = fig.get_facecolor()
        self.toolbar = QNavigationToolbar(self.canvas, self)

        self.toolbar.setStyleSheet("QNavigationToolbar { background-color: %s }"
                                   %rgb2hex(color))
        self.toolbar.setIconSize(QtCore.QSize(16, 16))
        self.canvas.mpl_connect('key_press_event', self.on_key_press)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.toolbar)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

    def close(self):
        super(QFigureWidget, self).close()

    def on_key_press(self, event):
        # sometimes mpl has a weird ideas what oo-programing is.
        # any could overwrite method by my self

        # no fullscreen unless self is a window!
        if event.key == "t":
            self.toolbar.toggle()
        elif event.key not in rcParams["keymap.fullscreen"]:
            key_press_handler(event, self.canvas, self.toolbar)
