"""
annotation_model.py

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ =("AtMultiClassSvmItemModel", )


from itertools import cycle
import numpy as np

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt

from annot.classifiers.itemclass import ItemClass
from .models import AtStandardItemModel


class DoubleAnnotationError(Exception):
    pass


class IncompleteAnnotationError(Exception):
    pass


class AtMultiClassSvmItemModel(AtStandardItemModel):

    ClassColumn = 0
    ColorColumn = 1
    ButtonColumn = 2

    classesChanged = QtCore.pyqtSignal(dict)

    _colors = ("#4daf4a", "#ffff33", "#ff7f00", "#f781bf", "#984ea3",
               "#377eb8", "#e41a1c", "#a65628", "#999999")

    def __init__(self, *args, **kw):
        super(AtMultiClassSvmItemModel, self).__init__(*args, **kw)
        self._item_classnames = dict()
        self._color_cycle = cycle(self._colors)
        self._reassign = False
        # only top level items are editable
        self.dataChanged.connect(self.onDataChanged)

    def _setHeader(self):
        # default columns
        self.setHeaderData(0, Qt.Horizontal, "class")
        self.setHeaderData(1, Qt.Horizontal, "color")
        self.setHeaderData(2, Qt.Horizontal, "button")

    def _brushFromColor(self, color):
        color = QtGui.QColor(color)
        brush = QtGui.QBrush()
        brush.setColor(color)
        brush.setStyle(Qt.SolidPattern)
        return brush

    def allowReassign(self, state):
        self._reassign = (state == Qt.Checked)

    def clear(self):
        # reset the color cycle
        self._color_cycle = cycle(self._colors)
        # clear last classification result
        for item in self._items.values():
            item.clear()
        self._item_classnames.clear()
        super(AtMultiClassSvmItemModel, self).clear()

    def setData(self, index, value, role):

        if index.column() == self.ColorColumn:
            self.item(index.row(), index.column()).setBackground(
                self._brushFromColor(value))

        return super(AtMultiClassSvmItemModel, self).setData(index, value, role)

    def findClassItems(self, class_name, match=Qt.MatchExactly):

        items = super(AtMultiClassSvmItemModel, self).findItems(
            class_name, match, self.ClassColumn)

        if not items:
            raise RuntimeError("No Item with content '%s' found" %class_name)
        else:
            return items[0]

    def onDataChanged(self, topleft, bottomright):
        self.emitClassesChanged()

    def currentClasses(self):
        """Construct a class defintion from the model by iteration over
        the 'toplevel items'."""

        classes = dict()
        for i in range(self.rowCount()):
            class_item = self.item(i, self.ClassColumn)
            color_item = self.item(i, self.ColorColumn)

            name = class_item.text()
            color = color_item.text()
            classes[i] = ItemClass(name, QtGui.QColor(color), i)

        return classes

    def emitClassesChanged(self):
        """Read the class defintion and emit the 'classesChanged' signal.
        This method must be called whenever a class is add or remove or the
        name or color of a class has changed."""

        classes = self.currentClasses()
        self.classesChanged.emit(classes)

    def addClass(self, name='unnamed', color=None):

        if color is None:
            color = self._color_cycle.next()

        items = self.findItems(name, Qt.MatchStartsWith, self.ClassColumn)
        if items:
            name = ''.join([name, str(len(items))])
        elif name == "unnamed":
            name = "unnamed0"

        name_item = QtGui.QStandardItem(name)
        color_item = QtGui.QStandardItem(color)
        color_item.setBackground(self._brushFromColor(color))
        button_item = QtGui.QStandardItem()

        name_item.setEditable(True)
        color_item.setEditable(True)
        self.appendRow([name_item, color_item, button_item])

        self.parent().openPersistentEditor(
            self.index(self.rowCount()-1, self.ButtonColumn))

        self.layoutChanged.emit()
        self.emitClassesChanged()

    def removeClass(self, modelindex):

        # remove items from the bookkeeping dictionaries
        parent = self.item(modelindex.row(), 0)
        for row in range(parent.rowCount()-1, -1, -1):
            key = parent.child(row).data().toPyObject()
            self._items[key].clear()
            del self._items[key]
            del self._item_classnames[key]

        self.removeRow(modelindex.row())
        self.emitClassesChanged()

    def findChildIndex(self, hashvalue, class_item):
        for row in range(class_item.rowCount()):
            child = class_item.child(row)
            if child.data().toPyObject() == hashvalue:
                return child.index()

    def addAnnotation(self, item, class_name):
        """Add samples to class definitions. Distinguish 3 cases:

        1) sample is annotated the first time
        2) samplle is already annotated to an other class, but shall
           be reassigned.
        3) sample is already annotated and can't be reassigned
        """

        if not self._items.has_key(item.hash):
            self._items[item.hash] = item
            self._item_classnames[item.hash] = class_name
            class_item = self.findClassItems(class_name)
            childs = self.prepareRowItems(item)
            class_item.appendRow(childs)

        elif self._reassign:
            old_class = self._item_classnames[item.hash]
            oclass_item = self.findClassItems(old_class)
            index = self.findChildIndex(item.hash, oclass_item)

            childs = oclass_item.takeRow(index.row())
            class_item = self.findClassItems(class_name)
            class_item.appendRow(childs)
            self._item_classnames[item.hash] = class_name
        elif class_name != self._item_classnames[item.hash]:
            raise DoubleAnnotationError("Item %d already annotated as %s"
                                        %(item.index, class_name))

    # removeAnnoations
    def removeItems(self, indices):
        for index in indices:
            parent = self.item(index.parent().row(), 0)
            if parent is not None:
                key = parent.child(index.row()).data().toPyObject()
                self._items[key].clear()
                del self._items[key]
                del self._item_classnames[key]
                parent.removeRow(index.row())

    def iterItems(self, parent):
        for i in range(parent.rowCount()):
            key = parent.child(i).data().toPyObject()
            yield self._items[key]

    @property
    def labels(self):

        all_labels = np.array([])
        nfeatures = self.items[0].features.size
        classes = self.currentClasses()

        # class label equals row
        for label, class_ in classes.iteritems():
            parent = self.item(label, 0)
            nitems = parent.rowCount()
            labels = label*np.ones(nitems, dtype=int)
            all_labels = np.append(all_labels, labels)

        return all_labels

    @property
    def features(self):
        """Yields a feature matrix from the items in the Sidebar. One feature
        vector per row."""

        nclasses = self.rowCount()
        if not nclasses:
            return

        all_features = None
        nfeatures = self.items[0].features.size
        classes = self.currentClasses()

        # class label equals row
        for label, class_ in classes.iteritems():
            parent = self.item(label, 0)
            nitems = parent.rowCount()

            if not nitems:
                raise IncompleteAnnotationError(
                    "There are not samples annotated for class %s" %class_.name)

            features = np.empty((nitems, nfeatures))
            for i, item in enumerate(self.iterItems(parent)):
                features[i, :] = item.features
            try:
                all_features = np.vstack((all_features, features))
            except ValueError:
                all_features = features

        return all_features