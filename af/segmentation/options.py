"""
options.py

Default parameter (-classes) for segmenation

feature_groups - any feature group in the dict will be calculated
PrimaryParams, ExpansionParams - tuples to set up the segmenation
                                 cellcogntion segmenation plugins
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ["feature_groups", "PrimaryParams", "ExpansionParams", "SRG_TYPE"]

from collections import namedtuple
from cecog import ccore

# map symbolic constants to a dict. The keys go to the xml file
# i.e. it is easier to restore the settings
SRG_TYPE = {"CompleteGrow": ccore.SrgType.CompleteGrow,
            "KeepContours": ccore.SrgType.KeepContours,
            "KeepContoursPlus": ccore.SrgType.KeepContoursPlus}

feature_groups = {'granulometry': None,
                  'normbase': None,
                  'normbase2': None,
                  'roisize': None,
                  'circularity': None,
                  'irregularity': None,
                  'irregularity2': None,
                  'axes': None,
                  'distance': None,
                  'convexhull': None,
                  'moments': None,
                  'levelset':  None,
                  'haralick': (1, 2, 4, 8),
                  'haralick2':(1, 2, 4, 8)}


PrimaryParams = namedtuple(
    'PrimaryParams', ['median_radius',  'window_size', 'min_contrast',
                      'remove_borderobjects', 'fill_holes', 'norm_min',
                      'norm_max','size_min', 'size_max', 'intensity_min',
                      'intensity_max', 'gallery_size'])

ExpansionParams = namedtuple(
    'ExpansionParams', ['srg_type', 'label_number', 'region_statistics_array',
                        'expansion_size', 'sep_expansion_size',  'norm_min', 'norm_max'])
