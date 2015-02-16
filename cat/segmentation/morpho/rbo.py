"""
rbo.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('remove_border_objects', )


import numpy as np

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
