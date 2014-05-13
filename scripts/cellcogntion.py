"""
threshold.py

demo script for otsu threshold using cellcogntion framwork
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
import numpy as np

import vigra
from cecog import VERSION
from cecog.environment import CecogEnvironment
from cecog import ccore


class Segmentation(object):

    def __init__(self, image, mean_radius=3, window_size=42, min_contrast=3,
                 remove_borderojbects=True, fill_holes=True):
        self._mean_radius = mean_radius
        self._window_size = window_size
        self._min_contrast = min_contrast
        self._fill_holes = fill_holes
        self._rbo = remove_borderojbects
        self._image = ccore.numpy_to_image(image, copy=True)

    @property
    def label_image(self):
        return self._container.img_labels.toArray()

    def __call__(self):
        image = ccore.disc_median(self._image, self._mean_radius)
        seg_image = ccore.window_average_threshold(
            image, self._window_size, self._min_contrast)
        if self._fill_holes:
            ccore.fill_holes(seg_image)

        self._container = ccore.ImageMaskContainer(
            image, seg_image, self._rbo)


if __name__ == "__main__":

    environ = CecogEnvironment(VERSION, redirect=False, debug=False)
    if not vigra.impex.isImage(sys.argv[1]):
        SystemExit("File not found!")

    # form vigra to numpy to cecog image
    image0 = vigra.readImage(sys.argv[1])
    image0 = np.array(np.squeeze(image0.swapaxes(0, 1))).astype(np.uint8)

    seg = Segmentation(image0)
    seg()
    print seg._container

    # from pylab import *
    # figure()
    # imshow(seg.label_image/255.)
    # show()

    import pdb; pdb.set_trace()
