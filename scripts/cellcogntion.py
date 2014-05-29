"""
threshold.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import os
import sys
import vigra
import numpy as np

sys.path.append('..')
from af.imageio import LsmImage
from af.segmentation import ImageObject, ObjectDict
from af.segmentation.processing import PrimaryParams, ExpansionParams, feature_groups
from af.segmentation.multicolor import MultiChannelProcessor
from cecog import ccore

if __name__ == "__main__":

    if not os.path.isfile(sys.argv[1]):
        SystemExit("File not found!")

    lsm = LsmImage(sys.argv[1])
    lsm.open()
    image = lsm.toArray()

    params = {"Channel 1": PrimaryParams(3, 17, 3, True, True),
              "Channel 2" : ExpansionParams(
            ccore.SrgType.KeepContours, None, 0, 5, 0)}

    ftrg = {"Channel 1": feature_groups,
            "Channel 2": feature_groups}

    mp = MultiChannelProcessor(image, ["Channel 1", "Channel 2"])
    mp.segmentation(params)
    mp.calculateFeatures(ftrg)

    for label, obj in mp.objects.iteritems():
        print label, obj.bbox, obj.gallery_image.shape

    import pdb; pdb.set_trace()
