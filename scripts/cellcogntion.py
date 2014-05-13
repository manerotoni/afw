"""
threshold.py

demo script for otsu threshold using cellcogntion framwork
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import isfile
import numpy as np
import pylab

import vigra
from cecog import ccore
from scipy import ndimage


if __name__ == "__main__":
    plab.gray()
    if not vigra.impex.isImage(sys.argv[1]):
        SystemExit("File not found!")

    # form vigra to numpy to cecog image
    image0 = vigra.readImage(sys.argv[1])
    image0 = array(squeeze(image.swapaxes(0, 1))).astype(np.uint8)
    image0 = ccore.numpy_to_image(image, copy=True)

    figure()
    imshow(image0)
    draw()

    # prefilter step in cellcogntion primary plugin
    # parameter: median radius
    image1 = ccore.disc_median(image0, 3)
    figure()
    imshow(image1)
    draw()

    figure()
    # local adaptive threshold
    # parameters: window size and min contrast (threshold)
    image2 = ccore.window_average_threshold(image1, 42, 3)
    imshow(image1)
    draw()

    # hole filling:
    # parameters:
    image3 = ccore.fill_holes(image2, False)


    figure()
    # import pdb; pdb.set_trace()

    imshow(image)

    figure()
    imshow(image > thr)

    show()
