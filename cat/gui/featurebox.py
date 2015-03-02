"""
featurebox.py

Widget for selecting features groups. Currently there are 8 different
feature groups (same as in Cellcognition)

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('FeatureBox', )


from os.path import splitext

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore


class FeatureBox(QtGui.QGroupBox):
    """Widget for feature selection."""

    featuresChanged = QtCore.pyqtSignal(dict)

    def __init__(self, *args, **kw):
        super(FeatureBox, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)

        self.basicIntensityFeatures.stateChanged.connect(self.onFeatureChanged)
        self.basicShapeFeatures.stateChanged.connect(self.onFeatureChanged)
        self.convexHullFeatures.stateChanged.connect(self.onFeatureChanged)
        self.distanceMapFeatures.stateChanged.connect(self.onFeatureChanged)
        self.granulometryFeatures.stateChanged.connect(self.onFeatureChanged)
        self.haralickFeatures.stateChanged.connect(self.onFeatureChanged)
        self.moments.stateChanged.connect(self.onFeatureChanged)
        self.statisticalGeometricFeatures.stateChanged.connect(
            self.onFeatureChanged)

    def featureGroups(self):
        features = dict()

        if self.basicIntensityFeatures.isChecked():
            features["normbase"] = None
            features["normbase2"] = None

        if self.basicShapeFeatures.isChecked():
            features["roisize"] = None
            features["circularity"] = None
            features["irregularity"] = None
            features["irregularity2"] = None
            features["axes"] = None

        if self.convexHullFeatures.isChecked():
            features["convexhull"] = None

        if self.distanceMapFeatures.isChecked():
            features["distance"] = None

        if self.granulometryFeatures.isChecked():
            features["granulometry"] = None

        if self.haralickFeatures.isChecked():
            features["haralick"] = (1, 2, 4, 8)
            features["haralick2"] = (1, 2, 4, 8)

        if self.moments.isChecked():
            features["moments"] = None

        if self.statisticalGeometricFeatures.isChecked():
            features["levelset"] = None

        return features

    def onFeatureChanged(self, state):
        self.featuresChanged.emit(self.featureGroups())

    def setFeatureGroups(self, groups):

        self.basicIntensityFeatures.setChecked(
            "normbase" in groups or "normbase2" in groups)

        self.basicShapeFeatures.setChecked(
            "roisize" in groups or
            "circularity" in groups or
            "irregularity" in groups or
            "irregularity2" in groups or
            "axes" in groups)

        self.convexHullFeatures.setChecked("convexhull" in groups)
        self.distanceMapFeatures.setChecked("distance" in groups)
        self.granulometryFeatures.setChecked("granulometry" in groups)
        self.haralickFeatures.setChecked(
            "haralick" in groups or "haralick2" in groups)
        self.moments.setChecked("moments" in groups)
        self.statisticalGeometricFeatures.setChecked(
            "levelset" in groups)
