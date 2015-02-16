"""
lineedit.py

Custom lineedit with a clear button

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtLineEdit", )

from PyQt4 import QtGui
from PyQt4 import QtCore


class AtLineEdit(QtGui.QLineEdit):
    """QLineEdit with clear button, which appears when user enters text."""

    def __init__(self, *args, **kw):
        super(AtLineEdit, self).__init__(*args, **kw)

        self._button = QtGui.QToolButton(self)
        self._button.setIcon(QtGui.QIcon(":/oxygen/clear.png"))
        self._button.setStyleSheet('border: 0px; padding: 0px;')
        self._button.setCursor(QtCore.Qt.ArrowCursor)

        width = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        size = self._button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }'
                           %(size.width() + width + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(),
                                size.width() + width*2 + 2),
                            max(self.minimumSizeHint().height(),
                                size.height() + width*2 + 2))

        self.textChanged.connect(self.changed)
        self._button.clicked.connect(self.clear)
        self._button.hide()

    def resizeEvent(self, event):
        size = self._button.sizeHint()
        width = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self._button.move(self.rect().right() - width - size.width(),
                         (self.rect().bottom() - size.height() + 1)/2)
        super(AtLineEdit, self).resizeEvent(event)

    def changed(self, text):
        """Shows image if text is not empty."""
        if text:
            self._button.show()
        else:
            self._button.hide()



if __name__ == "__main__":
    import sys
    from cat import at_rc
    app = QtGui.QApplication(sys.argv)
    main = AtLineEdit()
    main.show()
    sys.exit(app.exec_())
