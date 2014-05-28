"""
processor.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import collections
import numpy as np
from cecog import ccore
from cecog.environment import CecogEnvironment

from af.segmentation import ImageObject, ObjectDict


feature_groups = {'granulometry': None,
                  'normbase': None,
                  'normbase2': None,
                  'roisize': None,
                  'circularity': None,
                  'irregularity': None,
                  'irregularity2': None,
                  'axes': None,
                  'distance': None,
                  'convexhull': None,
                  'moments': None,
                  'levelset':  None,
                  'haralick': (1, 2, 4, 8),
                  'haralick2':(1, 2, 4, 8)}


PrimaryParams = collections.namedtuple(
    "PrimaryParams", ['mean_radius',  'window_size', 'min_contrast',
                      'remove_borderobjects', 'fill_holes'])

ExpansionParams = collections.namedtuple(
    "ExpansionParams", ["srg_type", "label_number", "region_statistics_array",
                        "expansion_size", "sep_expansion_size"])


class ProcessorCore(object):

    _environ = CecogEnvironment(redirect=False, debug=False)

    def __init__(self, name, image):
        super(ProcessorCore, self).__init__()
        self.name = name
        self.image = image

    @property
    def label_image(self):
        return self._container.img_labels.toArray()

    def calculateFeatures(self, feature_groups):
        for group, params in feature_groups.iteritems():
            if params is None:
                self._container.applyFeature(group)
            else: # special case for haralick features
                for param in params:
                    self._container.haralick_distance = param
                    self._container.applyFeature(group)

    @property
    def objects(self):
        odict = ObjectDict(self.name)
        for label, cobj in self._container.getObjects().iteritems():
            obj = ImageObject(cobj, self._container.getCrackCoordinates(label), label)
            obj.gallery_image = self._gallery_image(obj.center, gallery_size=50)
            odict[label] = obj
        return odict

    def _gallery_image(self, center, gallery_size=50):
        height, width = self.image.shape
        halfsize = np.floor(gallery_size/2.0)

        xmin = center.x - halfsize
        xmax = xmin + gallery_size
        ymin = center.y - halfsize
        ymax = ymin + gallery_size

        if xmin < 0:
            xmin = 0
            xmax = gallery_size
        elif xmax >= width:
            xmin = width - gallery_size
            xmax = width

        if ymin < 0:
            ymin = 0
            ymax = gallery_size
        elif ymax >= height:
            ymin = height - gallery_size
            ymax = height

        gimg = self.image[ymin:ymax, xmin:xmax]
        assert (gallery_size, gallery_size) == gimg.shape

        return gimg


class PrimaryProcessor(ProcessorCore):

    def __init__(self, name, image):
        super(PrimaryProcessor, self).__init__(name, image)

    def segmentation(self, mean_radius, window_size, min_contrast,
                     remove_borderobjects, fill_holes):

        image = ccore.numpy_to_image(self.image, copy=True)
        image = ccore.disc_median(image, mean_radius)
        seg_image = ccore.window_average_threshold(
            image, window_size, min_contrast)

        if fill_holes:
            ccore.fill_holes(seg_image)

        self._container = ccore.ImageMaskContainer(
            image, seg_image, remove_borderobjects)


class ExpandedProcessor(ProcessorCore):

    def __init__(self, name, image):
        super(ExpandedProcessor, self).__init__(name, image)

    def segmentation(self, label_image, srg_type, label_number,
                     region_statistics_array=0,
                     expansion_size=1,
                     sep_expansion_size=0):

        n_objects = label_image.max() + 1
        image = ccore.numpy_to_image(self.image, copy=True)
        limage = ccore.numpy_to_image(label_image, copy=True)

        img_labels = ccore.seeded_region_expansion(image, limage,
                                                   srg_type,
                                                   n_objects,
                                                   region_statistics_array,
                                                   expansion_size,
                                                   sep_expansion_size)

        self._container = ccore.ImageMaskContainer( \
            image, img_labels, False, True, True)
