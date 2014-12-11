"""
expandedRegion.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import numpy
import vigra

def expandRegion(img_thr, labels, radius=1):

    img_exp = vigra.filters.discDilation(
        img_thr.astype(numpy.uint8), radius=radius)

    return labels*img_exp
