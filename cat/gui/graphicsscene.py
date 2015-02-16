"""
graphicsscene.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtGraphicsScene", )


from PyQt4 import QtGui
from PyQt4 import QtCore
from annot.gui.cellitem import Colors
from annot.gui.cellitem import PainterPathItem


class AtGraphicsScene(QtGui.QGraphicsScene):
    """GraphicsScene with customized selection functionality

    -) double-click -> selects a single item, unselects all other items
    -) Ctrl-button + left mouse buuton -> selects all items the mouse moved over
    -) Ctrl-button + mouse click -> selects the item clicked,
       keeps previous selection
    """

    def __init__(self, *args, **kw):
        super(AtGraphicsScene, self).__init__(*args, **kw)
        self._multiselect = False
        self._selector = None

    def mouseMoveEvent(self, event):

        if self._multiselect:
            path = self._selector.path()
            path.lineTo(event.scenePos())
            self._selector.setPath(path)

        try:
            item = self.items(event.scenePos())[-1]
        except IndexError:
            item = None

        if (event.modifiers() == QtCore.Qt.ControlModifier and
            item is not None and
            self._multiselect):
            item.setSelected(True)
        else:
            super(AtGraphicsScene, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton:
            self._multiselect = True

        if event.button() == QtCore.Qt.RightButton:
            return
        elif event.modifiers() == QtCore.Qt.ControlModifier:
            pen = QtGui.QPen()
            pen.setColor(Colors.selected)
            pen.setWidth(3)
            pen.setJoinStyle(QtCore.Qt.RoundJoin)
            path = QtGui.QPainterPath(event.scenePos())
            # currently the selector is only to guide the eye
            # selection occurs on hovering the items
            self._selector = PainterPathItem(path, scene=self)
            self._selector.setPen(pen)
            super(AtGraphicsScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._multiselect = False

        if self._selector is not None:
            self.removeItem(self._selector)
            self._selector = None

        super(AtGraphicsScene, self).mouseReleaseEvent(event)

    def optimizeSceneRect(self):
        """Set the scene rect to the smallest possibe rect that contains
        all items."""
        # slow according to qt-doc
        self.setSceneRect(self.itemsBoundingRect())

    def selectAll(self):
        for item in self.items():
            item.setSelected(True)

    def invertSelection(self):
        for item in self.items():
            item.setSelected(not item.isSelected())
