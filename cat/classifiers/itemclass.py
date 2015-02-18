"""
itemclass.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("ItemClass", "UnClassified")

import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


class ItemClass(QtCore.QObject):
    """Definiton of one single class, in terms of machine learing."""

    def __init__(self, name, color, label, score=0.0):
        self.color = color
        self.name = name
        self.label = label

        # can be prediction probability or distance measure
        self._score = score

    def __eq__(self, other):
        return self.label == other.label

    def __str__(self):
        return self.name

    @staticmethod
    def fromItemClass(itemclass):
        """Returns a new ItemClass instance cloned from an existing one."""
        return ItemClass(itemclass.name, itemclass.color, itemclass.label,
                         itemclass.score)

    def clone(self):
        return ItemClass.fromItemClass(self)

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

    @property
    def brush_trainingsample(self):
        brush = QtGui.QBrush()
        brush.setColor(self.color)
        if self.label is None:
            brush.setStyle(Qt.NoBrush)
        else:
            brush.setStyle(Qt.Dense5Pattern)
        return brush

    @property
    def score(self):
        if isinstance(self._score, dict):

            return self._score[self.label]
        else:
            return self._score

    @score.setter
    def score(self, value):
        self._score = value

    @score.deleter
    def score(self, value):
        del self._score



UnClassified = ItemClass("unclassified", QtGui.QColor("white"), 10**9)
