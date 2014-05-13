"""
threshold.py

demo script for otsu threshold using cellcogntion framwork
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import isfile
import numpy as np
from pylab import *

import vigra
from cecog import ccore
from scipy import ndimage


def histeq(image, nbins=256):
   """Histogram equalisation: same implementation as in skimage but for
   arbitrary bitdepth.
   """

   hist, bins = np.histogram(image.flatten(), nbins)
   cdf = hist.cumsum()
   tk = (nbins-1)*cdf/float(cdf[-1])

   # use linear interpolation of cdf to find new pixel values
   image2 = np.interp(image.flat, bins[:-1], tk)
   return np.round(image2, 0).astype(np.uint8).reshape(image.shape)

if __name__ == "__main__":
    if not vigra.impex.isImage(sys.argv[1]):
        SystemExit("File not found!")


    image = vigra.readImage(sys.argv[1])
    image = np.array(np.squeeze(image.swapaxes(0, 1))).astype(np.uint8)
    # image2 = histeq(image)

    newImage = ccore.numpy_to_image(image, copy=True)
    thr = 3 # ccore.get_otsu_threshold(newImage)

    image = ndimage.gaussian_filter(image, 2)
    # figure()
    # h = hist(image.flatten(), bins=256, normed=True)
    # h = hist(image2.flatten(), bins=256, normed=True)

    gray()
    imshow(image, interpolation=None)
    title("original")

    # figure()
    # imshow(image2, interpolation=None)
    # title("histeq")

    figure()
    imshow(image > thr, interpolation=None)
    title("segmentation")

    print thr
    show()
