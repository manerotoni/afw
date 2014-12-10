"""
watershed.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('watershed')

import numpy as np
import vigra
from scipy import ndimage
from rbo import remove_border_objects, seed_mask
from seeding import find_seeds


def watershed(image, image_thres):

    image_labels, _ = ndimage.measurements.label(image_thres)
    mask = image_labels.astype(bool)

    img_edt = ndimage.morphology.distance_transform_edt(image_thres)
    seeds, lmax_x, lmax_y = find_seeds(img_edt)
    mask *= seed_mask(image_labels, seeds)

    dist = img_edt.max() - img_edt
    dist -= dist.min()
    dist = np.round(dist/float(dist.ptp())*255).astype(np.uint8)

    img_watershed, lmax = vigra.analysis.watersheds(
        dist, method="Turbo", seeds=seeds.astype("uint32"))

    # removing unseeded objects and objects at the image border
    return img_watershed*mask


