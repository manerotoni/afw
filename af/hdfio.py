"""
hdfio.py

read data from cellh5 and hdffiles

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('HdfReader', )

import cellh5


class HdfCoord(dict):

    def __init__(self, plate, well, site, region):
        super(HdfCoord, self).__init__(plate=plate,
                                       well=well,
                                       site=site,
                                       region=region)

class HdfItem(object):

    __slots__ = ['image', 'contour', 'features']

    def __init__(self, image, contour, features):
        self.image = image
        self.contour = contour
        self.features = features


class HdfReader(cellh5.CH5File):

    _features_def_key = "/definition/feature/"

    _root_key = "/sample/%(zero)s" %{'zero': "0"}
    _plate_key = _root_key + "/plate/%(plate)s"
    _well_key =  _plate_key + "/experiment/%(well)s"
    _site_key = _well_key + "/position/%(site)s"
    _features_key = _site_key + "/feature/%(region)s/object_features"


    def __init__(self, *args, **kw):
        super(HdfReader, self).__init__(*args, **kw)
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
        path = "%s/%s/object_features" %(self._features_def_key, region)
        return self._hdf[path]["name"]

    def numberItems(self, coordinate):
        path = self._features_key %coordinate
        return self._hdf[path].shape[0]

    def events(self, plate, well, site, region):
        site = self._open_position(plate, well, site)
        return site.get_events().flatten()

    def loadItem(self, index, coord, size=50):
        path = self._features_key %coord
        site = self._open_position(coord['plate'], coord['well'], coord['site'])
        gal = site.get_gallery_image(index, coord['region'], size)
        cnt = site.get_crack_contour(index, coord['region'], size=size)
        ftr = self._hdf[path][index]
        return HdfItem(gal, cnt[0], ftr)

    def iterEventGallery(self, plate, well, site, region, size=50):
        site = self._open_position(plate, well, site)
        events = site.get_events().flatten()

        for event in events:
            gal = site.get_gallery_image(event, region, size)
            cont = site.get_crack_contour(event, region, size=size)
            yield gal, cont[0]
