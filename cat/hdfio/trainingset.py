"""
traininset.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("AtTrainingSetIO", )


import numpy as np
from annot.hdfio.readercore import HdfFile, HdfFileInfo, HdfItem
from annot.hdfio.hdfwriter import HdfDataModel


class AtTrainingSetIO(HdfFile):
    """Reader and writer for the annotation tool trainingset data. The file
    format is a simple hdf5.
    """

    EXTENSIONS = (".hdf5", ".hdf", ".h5")
    GALLERY_SETTINGS_MUTABLE = False

    def __init__(self, *args, **kw):
        super(AtTrainingSetIO, self).__init__(*args, **kw)

        tset = self.attrs[HdfDataModel.TRAININGDATA][0]
        self.dmodel = HdfDataModel(tset)

    @property
    def settings(self):
        try:
            return self[self.dmodel.settings].value
        except KeyError:
            return self[self.dmodel.Legacy.settings].value

    @property
    def fileinfo(self):

        cspace = self.cspace()
        cspace = {'plate': cspace.keys(),
                  'well': cspace.values()[0].keys(),
                  'site': cspace.values()[0].values()[0].keys(),
                  'region': cspace.values()[0].values()[0].values()[0]}

        return HdfFileInfo(self.GALLERY_SETTINGS_MUTABLE,
                           self.numberItems(), self.gsize, cspace,
                           self.channelNames)

    @property
    def channelNames(self):
        channels = self[self.dmodel.contours].attrs[self.dmodel.CHANNELS]
        channels = [str(c) for c in channels]
        return tuple(channels)

    @property
    def gsize(self):
        # default size of a gallery image
        return self[self.dmodel.gallery].shape[0]

    def imageSize(self):
        return self[self.dmodel.images].shape[:2]

    # XXX set attributes to hdffile
    def numberItems(self, coordinate=None):
        return self[self.dmodel.bbox].shape[0]

    def featureNames(self, region=None):
        return self[self.dmodel.features].dtype.names

    def _transposeAndClip(self, contours):
        cnts = list()
        for i, cnt in enumerate(contours):
            x = np.clip(cnt[0], 0, self.gsize)
            y = np.clip(cnt[1], 0, self.gsize)
            cnts.append(zip(x, y))
        return cnts

    def _getAllContours(self, dtable):

        hsize = np.floor(self.gsize/2.0)
        channels = self[self.dmodel.contours].attrs[self.dmodel.CHANNELS]
        # shift centers to the bottom left corner of the gallery image
        center = np.vstack((dtable["x"], dtable["y"])).T - hsize

        height, width = self.imageSize()
        center[center[:, 0]<0, 0] = 0
        center[center[:, 0]>(width-self.gsize), 0] = width - self.gsize
        center[center[:, 1]<0, 1] = 0
        center[center[:, 1]>(height-self.gsize), 1] = height - self.gsize

        contours = list()
        for channel in channels:
            cnt = self[self.dmodel.contours+"/%s" %channel].value
            cnt = cnt - center
            cnt = self._transposeAndClip(cnt)
            contours.append(cnt)

        contours = np.swapaxes(contours, 0, 1)
        return contours.tolist()


    def iterItems(self, *args, **kw):
        # need *magic for compatibiliy to other classes

        cols = self[self.dmodel.images].attrs[self.dmodel.COLORS]
        cols = [str(c) for c in cols] # no unicode

        gal = self[self.dmodel.gallery].value
        datatbl = self[self.dmodel.bbox].value
        cnts = self._getAllContours(datatbl)
        ftrs = self[self.dmodel.features].value

        # dtype read from hdf does not work for sorting, need an 2d table
        ftrs = ftrs.view(dtype=np.float32).reshape(ftrs.shape[0], -1)

        for i in xrange(gal.shape[3]):
            yield HdfItem(gal[:, :, :, i], cnts[i], ftrs[i], index=i,
                          objid=datatbl["label"][i], frame=i, colors=cols,
                          path=self.dmodel.features)
