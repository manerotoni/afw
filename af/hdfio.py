"""
hdfio.py

read data from cellh5 and hdffiles

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('HdfReader', )

import cellh5


class HdfReader(cellh5.CH5File):

    _feature_def_key = "/definition/feature/"

    _root_key = "/sample/%(zero)s" %{'zero': "0"}
    _plate_key = _root_key + "/plate/%(plate)s"
    _well_key =  _plate_key + "/experiment/%(well)s"
    _site_key = _well_key + "/position/%(site)s"

    sample_str = "/sample/%s/plate/%s/experiment/%s/position"

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
        return self._hdf[self._feature_def_key].keys()

    def iterEventGallery(self, plate, well, site, region, size=50):
        site = self._open_position(plate, well, site)
        events = site.get_events().flatten()

        for event in events:
            gal = site.get_gallery_image(event, region, size)
            cont = site.get_crack_contour(event, region, size=size)
            yield gal, cont[0]
