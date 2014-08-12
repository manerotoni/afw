"""
mp_importer.py

demo script which uses pythons multiprocessing for segmentation

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
sys.path.append("../")


import time
import os
# from os.path import basename

import argparse
import numpy as np
from collections import OrderedDict

from cecog import ccore
from af.hdfio.hdfwriter import HdfWriter
from af.segmentation import LsmProcessor
from af.segmentation import PrimaryParams, ExpansionParams
from af.segmentation import ObjectDict

from multiprocessing import Pool, Manager


class Params(object):

    gsize =  50
    channels = OrderedDict(((0, 'Channel 1'), ))#,  (1, 'Channel 2')))

    seg_params = OrderedDict([('Channel 1',
                               PrimaryParams(3, 20, 5, True, True, 0, 255, 200,
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
    colors = [params.colors[c] for c in params.channels.values()]
    writer.setupFile(len(files), params.channels, colors)
    writer.saveSettings(params.seg_params, params.feature_groups)

    pool = Pool(processes=8)#, initializer=initfunc, initargs=("Hello world!", ))
    fprm = zip(files, len(files)*[params])
    result = pool.map(process_image, fprm)

    for i, (image, image_objects, feature_names) in enumerate(result):
        # reconstruct the ObjectDict
        objects = ObjectDict("multicolor")
        objects.feature_names = feature_names
        for obj in image_objects:
            objects[obj.label] = obj

        writer.saveData(objects, image)
    writer.flush()

def process_image((file_, params)):

    mp = LsmProcessor(file_, params.gsize)
    mp.segmentation(params.seg_params, params.channels)
    mp.calculateFeatures(params.feature_groups)
    image = mp.image[:, :, params.channels.keys()]
    objects = mp.objects
    # cannot return OrderedDict from multiprocessing, so I split the dict
    # and reconstruct it in the main process
    return (image, objects.values(), objects.feature_names)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Importer using multiprocessing')
    parser.add_argument("files", nargs="+", help="lsm files to be imported")
    parser.add_argument("outfile", help="Output file (hdf format)")

    args = parser.parse_args()

    t0 = time.time()
    import_images(args.files, args.outfile, Params)

    print ("%d images were processed in %.2f seconds"
           %(len(args.files), time.time()-t0))
