"""
cellh5.py

read data from cellh5 and hdffiles

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('Ch5Reader', 'Ch5Coord', 'HdfItem')


import cellh5
from af.hdfio import HdfBaseReader, HdfItem


class Ch5Coord(dict):
    """Custom mapping allowing only the following keys:
    plate, well, site and region.
    """

    _keys = ('plate', 'well', 'site', 'region')

    def __init__(self, plate, well, site, region):
        super(Ch5Coord, self).__init__(plate=plate, well=well,
                                       site=site, region=region)

    def __getitem__(self, key):
        if key not in self._keys:
            raise KeyError('Key is invalid')
        return super(Ch5Coord, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key not in self._keys:
            raise KeyError('Key is invalid')
        return super(Ch5Coord, self).__setitem__(key, value)


class Ch5Reader(HdfBaseReader, cellh5.CH5File):

    EXTENSIONS = (".ch5", )

    _features_def_key = "/definition/feature/"

    _root_key = "/sample/%(zero)s" %{'zero': "0"}
    _plate_key = _root_key + "/plate/%(plate)s"
    _well_key =  _plate_key + "/experiment/%(well)s"
    _site_key = _well_key + "/position/%(site)s"
    _features_key = _site_key + "/feature/%(region)s/object_features"
    _time_key = _site_key + "/object/%(region)s"
    _timelapse_key = _site_key + "/image/time_lapse"

    def __init__(self, *args, **kw):
        super(Ch5Reader, self).__init__(*args, **kw)
        self._hdf = self._file_handle

    def plateNames(self):
        key = self._plate_key %{"plate": ""}
        return self._hdf[key].keys()

    def wellNames(self, coords):
        assert coords.has_key("plate")
        coords["well"] = ""
        key = self._well_key %coords
        return self._hdf[key].keys()

    def siteNames(self, coords):
        assert coords.has_key("plate")
        assert coords.has_key("well")
        coords["site"] = ""
        key = self._site_key %coords
        return self._hdf[key].keys()

    def regionNames(self):
        return self._hdf[self._features_def_key].keys()

    def featureNames(self, region):
        path = "%s/%s/objcect_features" %(self._features_def_key, region)
        return self._hdf[path]["name"]

    def numberItems(self, coordinate):
        path = self._features_key %coordinate
        return self._hdf[path].shape[0]

    def cspace(self):
        """Returns a full mapping of the coordiante space the hdf file"""

        # plate, well and site point to one single movie. each movie
        # can have different segementation regions.

        coord = dict()
        coorddict = dict()
        plates = self.plateNames()

        # read regions from definition
        regions = self.regionNames()

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

    def loadItem(self, index, coord, size=50):

        path = self._features_key %coord
        site = self._open_position(coord['plate'], coord['well'], coord['site'])
        gal = site.get_gallery_image(index, coord['region'], size)
        cnt = site.get_crack_contour(index, coord['region'], size=size)
        ftr = self._hdf[path][index]

        # inefficient!
        path = self._time_key %coord
        fidx, objid = self._hdf[path][index]
        frame = self._hdf[self._timelapse_key %coord]["frame"][fidx]

        return HdfItem(gal, cnt[0], ftr, objid, frame)
