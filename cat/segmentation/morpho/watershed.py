"""
watershed.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('watershed', )

import numpy as np
import vigra
from scipy import ndimage
from seeding import find_seeds, seed_mask


def watershed(image_thres, seeding_size=5):

    image_labels, _ = ndimage.measurements.label(image_thres)
    mask = image_labels.astype(bool)

    img_edt = ndimage.morphology.distance_transform_edt(image_thres)
    seeds, lmax_x, lmax_y = find_seeds(img_edt, seeding_size)
    mask *= seed_mask(image_labels, seeds)

    dist = img_edt.max() - img_edt
    dist -= dist.min()
    dist = np.round(dist/float(dist.ptp())*255).astype(np.uint8)

    img_watershed, lmax = vigra.analysis.watersheds(
        dist, method="Turbo", seeds=seeds.astype("uint32"))

    # removing unseeded objects and objects at the image border
    return img_watershed*mask
