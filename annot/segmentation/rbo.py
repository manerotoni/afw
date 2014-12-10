"""
rbo.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy as np
from scipy import ndimage

def remove_border_objects(label_image, margin=1):
    """Remove objects from a label image that touch the image border.
    The default margin is 1 pixel.
    """

    labels = np.hstack((label_image[:margin, :].flatten(),
                        label_image[-margin,:].flatten(),
                        label_image[:, :margin].flatten(),
                        label_image[:, -margin:].flatten()))

    labels = np.unique(labels)
    labels.sort()

    for label in labels:
        label_image[label_image == label] = 0

    return label_image


def seed_mask(label_image, seeds):
    # seeds image has not the same labeling, the position counts
    seed_labels = np.unique(label_image*seeds.astype(bool))
    labels = np.unique(label_image)
    nlabels = np.setdiff1d(labels, seed_labels)

    for nl in nlabels:
        label_image[label_image == nl] = 0

    return label_image.astype(bool)
