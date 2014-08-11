"""
mp_importer.py

demo script which uses pythons multiprocessing for segmentation

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
sys.path.append("../")

import time
from os.path import basename

import argparse
from collections import OrderedDict

from cecog import ccore
from af.hdfio.hdfwriter import HdfWriter
from af.segmentation import LsmProcessor
from af.segmentation import PrimaryParams, ExpansionParams

class Params(object):

    gsize =  50
    channels = OrderedDict(((0, 'Channel 1'), )) # (1, 'Channel 2')))

    seg_params = OrderedDict([('Channel 1',
                               PrimaryParams(3, 20, 5, True, True, 0, 255, -1,
                                             -1, -1, -1, 65)),
                              ('Channel 2',
                               ExpansionParams(ccore._cecog.SrgType.KeepContours,
                                               None, 0, 5, 0, 0, 255))])

    feature_groups = {'Channel 1': {'distance': None,
                                    'circularity': None,
                                    'convexhull': None,
                                    'haralick': (1, 2, 4, 8),
                                    'normbase2': None,
                                    'roisize': None,
                                    'axes': None,
                                    'irregularity2': None,
                                    'haralick2': (1, 2, 4, 8),
                                    'levelset': None,
                                    'granulometry': None,
                                    'moments': None,
                                    'normbase': None,
                                    'irregularity': None},
                      'Channel 2': {'distance': None,
                                    'circularity': None,
                                    'convexhull': None,
                                    'haralick': (1, 2, 4, 8),
                                    'normbase2': None,
                                    'roisize': None,
                                    'axes': None,
                                    'irregularity2': None,
                                    'haralick2': (1, 2, 4, 8),
                                    'levelset': None,
                                    'granulometry': None,
                                    'moments': None,
                                    'normbase': None,
                                    'irregularity': None}}

    colors = {"Channel 1": "#ff0000",
              "Channel 2": "#00ff00"}


def import_images(files, outfile, params):


    proc = LsmProcessor(files[0], params.gsize)
    metadata = proc.metadata
    writer = HdfWriter(outfile)
    writer.setupFile(len(files), params.channels, params.colors,
                     metadata.size, metadata.dtype)
    writer.saveSettings(params.seg_params, params.feature_groups)


    t0 = time.time()
    for i, file_ in enumerate(files):
        _, image, objects = process_image(file_, i, params)
        writer.saveData(objects)
        writer.setImage(image, i)
        print  i, time.time() - t0
        t0 = time.time()

    writer.flush()

def process_image(file_, index, params):
    mp = LsmProcessor(file_, params.gsize)
    mp.segmentation(params.seg_params, params.channels)
    mp.calculateFeatures(params.feature_groups)
    image = mp.image[:, :, params.channels.keys()]
    objects = mp.objects
    return (index, image, objects)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Importer using multiprocessing')
    parser.add_argument("files", nargs="+", help="lsm files to be imported")
    parser.add_argument("outfile", help="Output file (hdf format)")

    args = parser.parse_args()

    import_images(args.files, args.outfile, Params)
