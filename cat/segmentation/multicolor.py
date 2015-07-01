"""
multicolor.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ('MultiChannelProcessor', 'LsmProcessor')

import sys
import warnings
import numpy as np
from collections import OrderedDict

from qimage2ndarray import gray2qimage
import vigra
from cecog import ccore
from cecog.environment import CecogEnvironment

from cat.imageio import LsmImage, TiffImage
from cat.imageio.imagecore import ImageCore
from cat.segmentation import ObjectDict, ImageObject
from cat.segmentation.morpho import watershed
from cat.segmentation import ZProject

import mimetypes
mimetypes.add_type('image/lsm', '.lsm')


def zProjection(image, method, zslice=0):

    if method == ZProject.Maximum:
        return image.max(axis=ImageCore.Idx_z)
    elif method == ZProject.Mean:
        return image.mean(axis=ImageCore.Idx_z)
    elif method == ZProject.Minimum:
        return image.min(axis=ImageCore.Idx_z)
    elif method in (ZProject.Select, ZProject.MaxTotalIntensity):
        if image.ndim == 4:
            return image[:,  :, zslice, :]
        else:
            return image[:,  :, zslice]
    else:
        raise RuntimeError("Projection method not defined")


def outlineSmoothing(label_image, outline_smoothing):

    label_image = vigra.filters.discClosing(
        label_image, outline_smoothing)
    label_image = vigra.filters.discOpening(
        label_image, outline_smoothing)

    return label_image


class MultiChannelProcessor(object):

    _environ = CecogEnvironment(redirect=False, debug=False)

    def __init__(self, filename, params, channels,
                 gallery_size=60, treatment=None):
        super(MultiChannelProcessor, self).__init__()

        if not isinstance(params, OrderedDict):
            raise RuntimeError("Segmentation paramters must be ordered\n"
                               "cannot determine the primary channel")

        self.params = params
        self.channels = channels
        self.treatment = treatment
        self._image = None
        self._reader = None
        self._objects = None
        self.gsize = gallery_size
        self._filename = filename
        self._containers = OrderedDict()
        self._imaster = None
        self._zslice = None

    @property
    def zslice(self):
        if self._zslice is None:
            ppar = self.params.values()[0]
            if ppar.zprojection == ZProject.MaxTotalIntensity:
                self._zslice = np.argmax(
                    self.image[:,:,:, self.imaster].sum(axis=0).sum(axis=0))
            else:
                self._zslice = ppar.zslice
        return self._zslice

    @property
    def imaster(self):
        if self._imaster is None:
            # the master (primary) channel is determined by the first item
            # the segmentation parameters (OrderedDict)
            channels_r = OrderedDict([(v, k) for k, v in self.channels.items()])
            try:
                self._imaster = channels_r[self.params.keys()[0]]
            except KeyError:
                raise KeyError("Primary channel is deactivated!")
        return self._imaster

    @property
    def metadata(self):
        return self._reader.metadata

    def iterprops(self):
        return self._reader.iterprops()

    @property
    def image(self):
        if self._image is None:
            self._image = self._reader.toArray()
        return self._image

    @image.deleter
    def image(self):
        del self._image

    def iterQImages(self, all_channels=True, normalize=True):
        """Iterator over to qimage converted images, one qimage per channel."""
        if all_channels:
            channels = range(self._reader.channels)
        else:
            channels = self.channels.keys()

        zprojection = self.params.values()[0].zprojection

        for ci in channels:
            image = zProjection(self.image[:, :, :, ci], zprojection, self.zslice)
            yield gray2qimage(image, normalize=normalize)

    def _gallery_image(self, center, gallery_size=50):
        height, width, zslices, nchannels = self.image.shape
        halfsize = int(np.floor(gallery_size/2.0))

        xmin = center.x - halfsize
        xmax = xmin + gallery_size
        ymin = center.y - halfsize
        ymax = ymin + gallery_size

        if xmin < 0:
            xmin = 0
            xmax = gallery_size
        elif xmax >= width:
            xmin = width - gallery_size
            xmax = width

        if ymin < 0:
            ymin = 0
            ymax = gallery_size
        elif ymax >= height:
            ymin = height - gallery_size
            ymax = height

        zprojection = self.params.values()[0].zprojection

        gimg = self.image[ymin:ymax, xmin:xmax, :, self._channel_idx]
        gimg = zProjection(gimg, zprojection, self.zslice)
        return gimg

    @property
    def objects(self):
        if self._objects is None:
            odict = ObjectDict("multicolor")
            for i, (name, container) in enumerate(self._containers.iteritems()):
                for label, cobj in container.getObjects().iteritems():
                    obj = ImageObject(
                        name, cobj, container.getCrackCoordinates(label),
                        self.treatment, label)

                    if odict.has_key(label):
                        odict.concatenate(name, label, obj)
                    else:
                        # mulitchannel gallery image
                        obj.gallery_image = self._gallery_image(
                            obj.center, gallery_size=self.gsize)
                        odict[label] = obj

                # set feature names extend with a prefix
                try:
                    cn = name.split()[1]
                    odict.feature_names.extend(
                        ["ch%s-%s" %(cn, n) for n in obj.feature_names])
                except UnboundLocalError as e:
                    # empty image has no objects
                    pass

            removed = odict.remove_incomplete()
            if len(removed) > 0:
                warnings.warn("%d objects have been removed" %len(removed))
            self._objects = odict
        return self._objects

    def calculateFeatures(self, feature_groups):
        """Calculate the features per color channel."""

        for name, container in self._containers.iteritems():
            fgroups = feature_groups[name]
            for group, params in fgroups.iteritems():
                if params is None:
                    container.applyFeature(group)
                else: # special case for haralick features
                    for param in params:
                        container.haralick_distance = param
                        container.applyFeature(group)

    def segmentation(self):

        # needed for gallery images
        self._channel_idx = self.channels.keys()
        # the master (primary) channel is determined by the first item
        # the segmentation parameters (OrderedDict)
        # channels_r = OrderedDict([(v, k) for k, v in self.channels.items()])

        # try:
        #     imaster = channels_r[self.params.keys()[0]]
        # except KeyError:
        #     raise KeyError("Primary channel is deactivated!")

        # segment the master first
        cname = self.channels[self.imaster]
        # if self.params[cname].zprojection == ZProject.MaxTotalIntensity:
        #     self._zslice = np.argmax(
        #         self.image[:,:,:,imaster].sum(axis=0).sum(axis=0))
        # else:
        #     self._zslice = self.params[cname].zslice

        image = zProjection(self.image[:, :, :, :].copy(),
                            self.params[cname].zprojection, self.zslice)

        self._containers[cname] = \
            self.threshold(image[:, :, self.imaster], **self.params[cname]._asdict())

        label_image = self._containers[cname].img_labels.toArray()
        self._filter(self._containers[cname], self.params[cname])

        for i, name in self.channels.iteritems():
            if i == self.imaster:
                continue

            self._containers[name] = self.seededExpandedRegion(
                image[:, :, i], label_image, *self.params[name])

    def threshold(self, image, median_radius, window_size, min_contrast,
                  remove_borderobjects, fill_holes, norm_min=0, norm_max=255,
                  use_watershed=True, seeding_size=5, outline_smoothing=1,
                  *args, **kw):

        image = self.normalize(image, norm_min, norm_max)
        image = ccore.numpy_to_image(image, copy=True)

        image_smoothed = ccore.gaussianFilter(image, median_radius)

        label_image = ccore.window_average_threshold(
            image_smoothed, window_size, min_contrast)

        if fill_holes:
            ccore.fill_holes(label_image)

        if outline_smoothing >= 1:
            label_image = outlineSmoothing(label_image.toArray(),
                                           outline_smoothing)
            label_image = ccore.numpy_to_image(label_image, copy=True)


        if use_watershed:
            label_image = label_image.toArray().copy()
            label_image = watershed(label_image, seeding_size=seeding_size)
            label_image = ccore.numpy_to_image(
                label_image.astype(np.int16), copy=True)

            return ccore.ImageMaskContainer(image, label_image,
                                            remove_borderobjects, True, True)
        else:
            # a static type system sucks!
            return ccore.ImageMaskContainer(image, label_image,
                                            remove_borderobjects)



    def seededExpandedRegion(self, image, label_image, srg_type, label_number,
                             region_statistics_array=0,
                             expansion_size=1,
                             sep_expansion_size=0,
                             norm_min=0, norm_max=255):

        if label_number is None:
           label_number = label_image.max() + 1

        image = self.normalize(image, norm_min, norm_max)
        image = ccore.numpy_to_image(image, copy=True)
        limage = ccore.numpy_to_image(label_image, copy=True)

        img_labels = ccore.seeded_region_expansion(image, limage,
                                                   srg_type,
                                                   label_number,
                                                   region_statistics_array,
                                                   expansion_size,
                                                   sep_expansion_size)

        return ccore.ImageMaskContainer(image, img_labels, False, True, True)

    def normalize(self, image_, norm_min=0, norm_max=255, dtype=np.uint8):
        """Normalize input image to range and return image as dtype
        (numpy int-type).
        """

        iinfo = np.iinfo(dtype)
        range_ = iinfo.max - iinfo.min
        image = (image_.astype(np.float) - norm_min)/(norm_max - norm_min)*range_
        image = np.round(np.clip(image, iinfo.min, iinfo.max), 0).astype(np.uint8)
        return image

    def _filter(self, container, params):

        if params.size_min != -1 or params.size_max != -1:
            container.applyFeature("roisize")
            if params.size_max == -1:
                size = (params.size_min, sys.maxint)
            else:
                size = (params.size_min, params.size_max)
        else:
            size = None


        if params.intensity_min != -1 or params.intensity_max != -1:
            container.applyFeature("normbase2")
            if params.intensity_max == -1:
                intensity = (params.intensity_min, sys.maxint)
            else:
                intensity = (params.intensity_min, params.intensity_max)
        else:
            intensity = None

        # nothing to filter
        if size is None and intensity is None:
            return

        for label, obj in container.getObjects().iteritems():
            features = obj.getFeatures()
            if size is not None and \
                    not (size[0] <= features['roisize'] <= size[1]):
                container.delObject(label)
            elif intensity is not None and \
                    not(intensity[0] <= features["n2_avg"] <= intensity[1]):
                container.delObject(label)


class LsmProcessor(MultiChannelProcessor):

    def __init__(self, filename, params, channels,
                 gallery_size=50, treatment=None):
        super(LsmProcessor, self).__init__(filename, params, channels,
                                           gallery_size, treatment)

        mtype = mimetypes.guess_type(filename)[0]

        if mtype == 'image/tiff':
            self._reader = TiffImage(filename)
        elif mtype == 'image/lsm':
            self._reader = LsmImage(filename)
        else:
            RuntimeError("Image format not supported %s" %str(mtype))
