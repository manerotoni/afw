"""
threshold.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
import vigra
import numpy as np

sys.path.append('..')
from af.segmentation import ImageObject, ObjectDict
from af.segmentation.processing import PrimaryParams, ExpansionParams, feature_groups
from af.segmentation.processing import ExpandedProcessor, PrimaryProcessor
from cecog import ccore

if __name__ == "__main__":

    if not vigra.impex.isImage(sys.argv[1]):
        SystemExit("File not found!")

    # form vigra to numpy to cecog image
    image = vigra.readImage(sys.argv[1])
    image = np.array(np.squeeze(image.swapaxes(0, 1))).astype(np.uint8)

    # mean radius, window_size, contrast, rbo, fill holes
    pparams = PrimaryParams(3, 42, 3, True, True)
    pp = PrimaryProcessor("Channel 1", image)
    pp.segmentation(*pparams)
    pp.calculateFeatures(feature_groups)

    for label, obj in pp.objects.iteritems():
        print label, obj.bbox, obj.gallery_image.shape

    image = vigra.readImage(sys.argv[2])
    image = np.array(np.squeeze(image.swapaxes(0, 1))).astype(np.uint8)

    eparams = ExpansionParams(ccore.SrgType.KeepContours, pp.label_image.max()+1, 0, 5, 0)
    ep = ExpandedProcessor("Channel 2", image)
    ep.segmentation(pp.label_image, *eparams)
    ep.calculateFeatures(feature_groups)

    for label, obj in ep.objects.iteritems():
        print label, obj.bbox, obj.gallery_image.shape


    import pdb; pdb.set_trace()
