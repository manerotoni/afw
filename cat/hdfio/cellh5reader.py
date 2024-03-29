"""
cellh5.py

read data from cellh5 and hdffiles

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('Ch5Reader', 'Ch5Coord', 'HdfItem')

import re
import zlib
import base64

import time
import numpy as np
from collections import OrderedDict
from cat.hdfio.readercore import HdfFile, HdfItem, HdfFileInfo
from cat.segmentation.channelname import ChannelName as cn
from cat.features import FGroup


# regular expressin that matches
#/sample/0/plate/H2b_aTub_MD20x_exp911/experiment/0/
# position/0037/feature/primary__primary/object_features

REGEX =("/sample/(?P<sample>\w)/plate/(?P<plate>\w*)"
        "/experiment/(?P<well>\w*)/position/(?P<site>\w*)"
        "/feature/(?P<region>\w*).*")


def uncompress_contour(contour):
    contour = np.asarray(zlib.decompress(
        base64.b64decode(contour)).split(','), dtype=np.int16)
    contour.shape = (-1, 2)
    return contour


def path2coord(path):
    """convert a cellh5 path (down to the feature table) into a Ch5Coord dict."""
    return re.match(REGEX, path).groupdict()


class Ch5Coord(dict):
    """Custom mapping allowing only the following keys:
    plate, well, site and region.
    """

    # sample is formerly part of the coordinates but is about
    # to be removed from cellh5
    SAMPLE = "0"

    _keys = ('sample', 'plate', 'well', 'site', 'region')

    def __init__(self, sample, plate, well, site, region):
        super(Ch5Coord, self).__init__(sample=sample, plate=plate, well=well,
                                       site=site, region=region)

    def __getitem__(self, key):
        if key not in self._keys:
            raise KeyError('Key is invalid')
        return super(Ch5Coord, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key not in self._keys:
            raise KeyError('Key is invalid')
        return super(Ch5Coord, self).__setitem__(key, value)


class Ch5Reader(HdfFile):

    EXTENSIONS = (".ch5", )
    GALLERY_SETTINGS_MUTABLE = True

    _features_def_key = "/definition/feature/"
    _image_def_key = "/definition/image"
    _channel_def_key = _image_def_key + "/channel"
    _region_name_key = _image_def_key + "/region"

    _root_key = "/sample/%(sample)s"
    _plate_key = _root_key + "/plate/%(plate)s"
    _well_key =  _plate_key + "/experiment/%(well)s"
    _site_key = _well_key + "/position/%(site)s"

    _features_key = _site_key + "/feature/%(region)s/object_features"
    _contours_key = _site_key + "/feature/%(region)s/crack_contour"
    _bbox_key = _site_key + "/feature/%(region)s/bounding_box"

    _time_key = _site_key + "/object/%(region)s"
    _timelapse_key = _site_key + "/image/time_lapse"
    _center_key = _site_key + "/feature/%(region)s/center"
    _image_key = _site_key + "/image/channel"

    _rname = "region_name"
    _channel_index = "channel_idx"
    _tidx = "time_idx"
    _feature_groups = "feature_groups"

    def __init__(self, *args, **kw):
        super(Ch5Reader, self).__init__(*args, **kw)

    @property
    def fileinfo(self):
        """Determines the default number of items to load (cellh5 files
        contain to many items to load them at once) and wether the size of
        the gallery images is fixed).
        """

        cspace = self.cspace()
        cspace = {'sample': [Ch5Coord.SAMPLE],
                  'plate': cspace.keys(),
                  'well': cspace.values()[0].keys(),
                  'site': cspace.values()[0].values()[0].keys(),
                  'region': cspace.values()[0].values()[0].values()[0]}

        return HdfFileInfo(self.GALLERY_SETTINGS_MUTABLE, 500, 65,
                           cspace, self.channelNames, self.colors)

    def featureGroups(self, region):
        """Return the feature groups as nested dictionaries.
        e.g. {channel: {meta_group: { group: (feature_list)}}}"""

        path = "%s/%s/object_features" %(self._features_def_key, region)

        fg = self[path]
        gmap = dict()
        for l in fg.attrs[self._feature_groups]:
            gmap[l[0]] = l[1]

        ftrs = fg.dtype.names[0]
        groups = fg.dtype.names[1:]

        channels = self.channelNames
        ch_groups = OrderedDict()

        for channel in channels:
            meta_group = OrderedDict()
            for group in groups:
                fgroup = FGroup(group, [(g, []) for g in np.unique(fg[group])])
                meta_group[gmap[group]] = fgroup
            ch_groups[channel] = meta_group

        for line in fg:
            fname = line[0]
            for channel in channels:
                for i, group in enumerate(groups):
                    ch_groups[channel][gmap[group]][line[i+1]].append(fname)
        return ch_groups

    # @property
    # def colors(self):
    #     colors = self[self._channel_def_key]['color']
    #     colors = [str(c) for c in colors]
    #     return tuple(colors)

    # @property
    # def channelNames(self):
    #     names = self[self._channel_def_key]['channel_name']
    #     names = [str(n) for n in names]
    #     return tuple(names)

    @property
    def colors(self):
        return ('#ffffff', )

    @property
    def channelNames(self):
        return ('Channel_1', )

    def plateNames(self):
        key = self._plate_key %{"sample": Ch5Coord.SAMPLE, "plate": ""}
        return self[key].keys()

    def wellNames(self, coords):
        assert coords.has_key("plate")
        coords["well"] = ""
        key = self._well_key %coords
        return self[key].keys()

    def siteNames(self, coords):
        assert coords.has_key("plate")
        assert coords.has_key("well")
        coords["site"] = ""
        key = self._site_key %coords
        return self[key].keys()

    def regionNames(self):
        return self[self._features_def_key].keys()

    def featureNames(self, region):
        path = "%s/%s/object_features" %(self._features_def_key, region)
        return ["ch1-%s" %s for s in self[path]["name"]]

    def numberItems(self, coordinate):
        path = self._features_key %coordinate
        return self[path].shape[0]

    def cspace(self):
        """Returns a full mapping of the coordiante space the hdf file"""

        # plate, well and site point to one single movie. each movie
        # can have different segementation regions.
        coord = dict()
        coorddict = dict()
        plates = self.plateNames()

        # read regions from definition
        regions = self.regionNames()

        # dummy for the "sample" variable
        coord['sample'] = Ch5Coord.SAMPLE

        for plate in plates:
            coord['plate'] = plate
            wells = self.wellNames(coord)
            coorddict.setdefault(plate, {})
            for well in wells:
                coord['well'] = well
                coorddict[plate].setdefault(well, {})
                sites = self.siteNames(coord)
                for site in sites:
                    coorddict[plate][well][site] = regions
        return coorddict

    def _gallery_image(self, coord, size, (height, width), (cx, cy), ci, ti):
        """Read position correceted gallery image"""

        hsize = int(np.floor(size/2.0))
        xmin = cx - hsize
        xmax = xmin + size
        ymin = cy - hsize
        ymax = ymin + size

        # correct image possition if gallery image close to the rim
        if xmin < 0:
            xmin = 0
            xmax = size
        elif xmax >= width:
            xmin = width - size
            xmax = width

        if ymin < 0:
            ymin = 0
            ymax = size
        elif ymax >= height:
            ymin = height - size
            ymax = height

        gimg = self[self._image_key %coord][ci, ti, 0, ymin:ymax, xmin:xmax]
        return  gimg

    def _contour(self, index, coord, size, (height, width), (cx, cy)):
        """Read position corrected contour"""

        hsize = int(np.floor(size/2.0))
        contour = self[self._contours_key %coord][index]
        contour = uncompress_contour(contour)

        # correct contour position if center is close to the rim
        if cx < hsize:
            cx = hsize
        elif cx > width - hsize:
            cx = width - hsize

        if cy < hsize:
            cy = hsize
        elif cy > height - hsize:
            cy = height - hsize

        contour[:, 0] -= cx - hsize
        contour[:, 1] -= cy - hsize
        contour = contour.clip(0, size)

        # no ndarrays to calculate the hash values
        contour =  [(x, y) for x, y in contour]
        return [contour]

    def iterItems(self, nitems, coord, size=50, delayed=True):

        nf = self.numberItems(coord)
        indices = range(0, nf)
        np.random.shuffle(indices)

        rname = self[self._region_name_key][self._rname].tolist()
        ci = self[self._region_name_key][self._channel_index]
        ci = ci[rname.index("region___%s" %coord['region'])]
        path = self._features_key %coord
        isize = self[self._image_key %coord].shape[3:5]
        tpath = self._time_key %coord
        tpath2 = self._timelapse_key %coord

        for index in indices[:nitems]:

            centers = self[self._center_key %coord][index]
            ti = self[self._time_key %coord][self._tidx][index]
            gal = self._gallery_image(coord, size, isize, centers, ci, ti)
            cnt = self._contour(index, coord, size, isize, centers)
            ftr = self[path][index]

            fidx, objid = self[tpath][index]
            frame = self[tpath2]["frame"][fidx]

            yield HdfItem(gal, cnt, ftr, index, objid, frame, path=path)
            if delayed:
                time.sleep(0.0035)

    def itemsFromClassifier(self, indices, paths, size=50):
        """List of HdfItems using a list of indices."""

        rname = self[self._region_name_key][self._rname].tolist()

        for index, path in zip(indices, paths):
            coord = path2coord(path)

            ci = self[self._region_name_key][self._channel_index]
            ci = ci[rname.index("region___%s" %coord['region'])]
            path = self._features_key %coord
            isize = self[self._image_key %coord].shape[3:5]
            tpath = self._time_key %coord
            tpath2 = self._timelapse_key %coord

            centers = self[self._center_key %coord][index]
            ti = self[self._time_key %coord][self._tidx][index]
            gal = self._gallery_image(coord, size, isize, centers, ci, ti)
            cnt = self._contour(index, coord, size, isize, centers)
            ftr = self[path][index]

            fidx, objid = self[tpath][index]
            frame = self[tpath2]["frame"][fidx]

            # cellh5 is so slow!
            yield HdfItem(gal, cnt, ftr, index, objid, frame, path=path)
