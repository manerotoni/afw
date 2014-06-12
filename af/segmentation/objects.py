"""
objects.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('ImageObject', 'ObjectDict')


import copy
from collections import namedtuple, OrderedDict
import numpy as np


Orientation = namedtuple("Orientation", ["angle", "excentricity"])
BBox = namedtuple("BBox", ["left", "right", "top", "bottom"])
Center = namedtuple("Center", ["x", "y"])
Class = namedtuple("Class", ["name", "label","color"])


class ImageObject(object):
    # Simple wrapper class for the c++ objects to python plus some
    # extra functinality.

    def __init__(self, name, cobj, contours_coords, label=None):

        self.name = name
        self.center = Center(cobj.oCenterAbs.x, cobj.oCenterAbs.y)
        self.bbox = BBox(cobj.oRoi.upperLeft.x, cobj.oRoi.lowerRight.x,
                         cobj.oRoi.upperLeft.y, cobj.oRoi.lowerRight.y)

        self.label  = label
        self.prediction_proba = {}
        self.class_= None
        self.contours = OrderedDict()

        ftrs = cobj.getFeatures()
        self.feature_names = sorted(ftrs.keys())
        self.features = np.array([ftrs[name] for name in self.feature_names])

        try:
            idx = self.feature_names.index("eccentricity")
            self.orientation = Orientation(cobj.orientation, self.features[idx])
        except AttributeError:
            self.orientation = None

        # contour coordinates are relative to the bbox, want them in
        # pixel coordinates
        self.contours[self.name] = [(x + self.bbox.left, y + self.bbox.top)
                                    for (x, y) in contours_coords]

    @property
    def contour(self):
        return self.contours[self.contours.keys()[0]]

    def setClass(self, name, label, color):
        self.class_ = Class(name, label, color)

    def featuresByName(self, feature_names):
        assert isinstance(feature_names, (list, tuple))
        idx = [self.feature_names.index(fn) for fn in feature_names]
        return self.features[idx]

    @property
    def featureNames(self):
        return self.features.dtype.names

    def distanceTo(self, x, y):
        return (float(x - self.center.x)**2 + float(y - self.center.y)**2)

    def touchesBorder(self, width, height):
        """Determines whether a region of interest touches the border
        given by width and height.
        """

        if (self.bbox.bottom > 0 and
            self.bbox.left > 0 and
            self.bbox.right < width-1 and
            self.bbox.top < height-1):
            return False
        else:
            return True


class ObjectDict(OrderedDict):
    """Container class for image objects. Provides object access by label (key),
    and the possibility to concatenate features of different object with
    the same label.
    """

    def __init__(self, name):
        super(ObjectDict, self).__init__()
        self.name = name
        self.feature_names = list()

    @property
    def contours(self):
        """Return a dictionary of the contours only."""
        cnt = dict()
        for key, value in self.iteritems():
            cnt[key] = value.contours
        return cnt

    @property
    def gallery_shape(self):
        obj = self[self.keys()[0]]
        return obj.gallery_image.shape + (len(self), )

    @property
    def gallery_dtype(self):
        obj = self[self.keys()[0]]
        return obj.gallery_image.dtype

    def copyObjects(self, objectdict):
        """Deepcopy image objects from one holder to self. Feature names must be
        provides separatly.
        """

        for label, obj in objectdict.iteritems():
            self[label] = copy.deepcopy(obj)

    @property
    def nfeatures(self):
        return len(self.feature_names)

    def remove_incomplete(self):
        """Remove samples that do not have the same number of features as
        required. This can happen in merged channels. i.e. where features of
        different processing channels are concatenated and the sample was
        skipped in on channel for some reason.
        """
        removed = list()
        for label, sample in self.items():
            if sample.features.size != self.nfeatures:
                del self[label]
                removed.append(label)
        return removed

    def concatenate(self, name, label, object_):
        """Concatenate features of image objects. If the dict does not contain
        the image object, it's added automatically.
        """

        obj = self[label]
        obj.features = np.append(obj.features, object_.features)
        obj.contours[object_.name] = object_.contour
