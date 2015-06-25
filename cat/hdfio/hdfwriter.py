"""
hdfwriter.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('HdfWriter', 'HdfDataModel', )


import time
import h5py
import numpy as np
from collections import defaultdict

from cat.config import AtConfig
from cat.xmlconf import XmlConfWriter
from cat.features import FeatureGroups

from cat.segmentation.channelname import ChannelName as cn

class HdfDataModel(object):

    TRAININGDATA = "training_data"
    COLORS = "colors"
    CHANNELS = "channels"

    # XXX remove this in later versions
    class Legacy(object):
        settings = "settings"

    def __init__(self, data=None):

        if data is None:
            self.data = "/data_%s" %time.strftime("%Y%m%d-%H%M%S")
        else:
            self.data = data

        self.images = "%s/images" %self.data
        self.contours = "%s/contours" %self.data
        self.gallery = "%s/gallery" %self.data
        self.bbox = "%s/bbox" %self.data
        self.features = "%s/features" %self.data
        self.feature_groups = "%s/feature_groups" %self.data
        self.settings = "/settings/segmentation"


class HdfCache(object):
    """Internal cache to be able to save non-resizeable data sets to hdf5."""

    def __init__(self, feature_names, gallery_dtype, colors):

        self.gallery = None
        self.bbox = None
        self.features = None
        self.images = None
        self.contours = defaultdict(list)
        self.colors = colors
        self._images = list()

        self.feature_names = feature_names
        self._dt_gallery = gallery_dtype
        self._dt_bbox = [('treatment', "S128"), ('label', np.uint32),
                         ('x', np.uint16), ('y', np.uint16), ('top', np.uint16),
                         ('bottom', np.uint16), ('left', np.uint16),
                         ('right', np.uint16)]

        self._dt_features = [(str(n), np.float32) for n in feature_names]
        self._dt_contours = h5py.special_dtype(vlen=np.uint16)
        self._dt_groups = [('feature', "S64")] + \
            [(str(g), "S64") for g in FeatureGroups.keys()]

        # setup the table of feature groups
        self.fgroups = np.empty((len(feature_names), ), dtype=self._dt_groups)
        for i, fname in enumerate(feature_names):
            line = [fname]

            for v in FeatureGroups.values():
                fname2 = cn.splitFeatureName(fname)[1]
                line.append(v.inverse[fname2])
            line = tuple([str(l) for l in line])

            self.fgroups[i] = np.array(line, dtype=self._dt_groups)

    def appendData(self, objectsdict, image):
        nobj = len(objectsdict)
        nftrs = len(objectsdict.feature_names)

        bbox = np.empty((nobj, ), dtype=self._dt_bbox)
        features = np.empty((nobj, ), dtype=self._dt_features)
        gallery = np.empty(objectsdict.gallery_shape, dtype=self._dt_gallery)

        # need to cast to the correct type
        for i, (label, obj) in enumerate(objectsdict.iteritems()):
            bbox[i] = np.array(
                (str(obj.treatment), label) + obj.center + obj.bbox,
                dtype=self._dt_bbox)
            features[i] = obj.features.astype(np.float32)
            gallery[:, :, :, i] = obj.gallery_image.astype(np.uint16)

            for cname, contour in obj.contours.iteritems():
                self.contours[cname].append((np.array(contour).T).tolist())

        if self.bbox is self.features is self.gallery:
            self.bbox = bbox
            self.features = features
            self.gallery = gallery
        else:
            self.bbox = np.append(self.bbox, bbox)
            self.features = np.append(self.features, features)
            self.gallery = np.concatenate((self.gallery, gallery), axis=3)

        self._images.append(image)

    @property
    def image(self):
        shape = self._images[0].shape + (len(self._images), )
        images = np.empty(shape, self._images[0].dtype)

        for i, image in enumerate(self._images):
            images[:, :, :, :, i] = image

        return images


class HdfWriter(object):


    def __init__(self, filename):
        self._file = h5py.File(filename, "w")
        self._cache = None
        self._compression = AtConfig().compression
        self._copts = AtConfig().compression_opts
        self.dmodel = HdfDataModel("data")

        # save a list of the training sets as attrib of the file
        if self.dmodel.TRAININGDATA in self._file.attrs.keys():
            tsets = self._file.attrs[self.dmodel.TRAININGDATA].tolist()
            tsets.append(self.dmodel.data)
        else:
            tsets = self.dmodel.data
            self._file.attrs[self.dmodel.TRAININGDATA] = [tsets, ]

    def close(self):
        self._file.close()

    def setupFile(self, n_images, channels, colors):

        grp = self._file.create_group(self.dmodel.contours)
        grp.attrs[HdfDataModel.CHANNELS] = [str(c.replace(" ", "_"))
                                       for c in channels.values()]
        self._colors = colors

    def saveSettings(self , segmentation, features, active_channels, colors):
        xml = XmlConfWriter(segmentation, features, active_channels, colors)
        txt = xml.toString()
        dset = self._file.create_dataset(self.dmodel.settings, data=txt)

    def saveData(self, objectsdict, image):
        # sometimes there are not objects found in an image
        # and objectsdict is empty
        if objectsdict:
            if self._cache is None:
                self._cache = HdfCache(objectsdict.feature_names,
                                       objectsdict.gallery_dtype,
                                       self._colors)
            self._cache.appendData(objectsdict, image)

    def _writeContours(self):

        for cname, contours in self._cache.contours.iteritems():
            path = "%s/%s" %(self.dmodel.contours, cname.replace(" ", "_"))

            # h5py seems to be buggy, cannot set contours directly,
            dset = self._file.create_dataset(
                path, (len(contours), 2, ), dtype=self._cache._dt_contours,
                compression=self._compression, compression_opts=self._copts)
            for i, cnt in enumerate(contours):
                dset[i, :] = cnt

    def flush(self):

        # hdf5 allows only 64kb of header metadata
        try:
            dset = self._file.create_dataset(
                self.dmodel.bbox, data=self._cache.bbox,
                compression=self._compression, compression_opts=self._copts)
            dset = self._file.create_dataset(
                self.dmodel.features, data=self._cache.features,
                compression=self._compression, compression_opts=self._copts)
            dset = self._file.create_dataset(
                self.dmodel.gallery, data=self._cache.gallery,
                chunks=(self._cache.gallery.shape[:2] + (1, 1)),
                compression=self._compression, compression_opts=self._copts)
            dset = self._file.create_dataset(
                self.dmodel.feature_groups, data=self._cache.fgroups,
                compression=self._compression, compression_opts=self._copts)
            self._writeContours()

            images = self._cache.image
            chunksize = images.shape[:2] + (1, 1, 1)
            dset = self._file.create_dataset(self.dmodel.images,
                                             data=images,
                                             chunks=chunksize,
                                             compression=self._compression,
                                             compression_opts=self._copts)
            dset.attrs[HdfDataModel.COLORS] = [str(c) for c in self._cache.colors]

        except ValueError as e:
            if "Object header message is too large" in str(e):
                raise HdfError("Cannot save data to hdf file."
                                 "One of you tables is to large, "
                                 "reduce number of channels")
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HdfError(str(e))
