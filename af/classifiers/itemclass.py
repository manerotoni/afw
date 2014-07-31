"""
itemclass.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("ItemClass", "UnClassified")


from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import Qt


class ItemClass(QtCore.QObject):
    """Definiton of one single class, in terms of machine learing."""

    def __init__(self, name, color, label):
        self.color = color
        self.name = name
        self.label = label

    def __eq__(self, other):
        return self.label == other.label

    def __str__(self):
        return self.name

    @property
    def pen(self):
        pen = QtGui.QPen()
        pen.setColor(self.color)
        return pen

    @property
    def brush(self):
        brush = QtGui.QBrush()
        brush.setColor(self.color)
        if self.label is None:
            brush.setStyle(Qt.NoBrush)
        else:
            brush.setStyle(Qt.SolidPattern)
        return brush

UnClassified = ItemClass("unclassified", QtGui.QColor("white"), None)
