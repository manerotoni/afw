"""
multicolor.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

from cecog import ccore


class MultiChannelProcessor(object):

    def __init__(self, image, channel_names, master_channel=None):

        if master_channel is None:
            self._master_channel = 0
        elif master_channel not in channel_names:
            raise RuntimeError("master channel not in list of channels")
        else:
            self._master_channel = channel_names.index(master_channel)

        self.image =  image
        self.cnames = channel_names
        self._master_channel = master_channel
        self._containers = dict()

    def calculateFeatures(self, feature_groups):
        """Calculate the features per color channel."""

        for name, container in self._containers.iteritems():
            fgroups = feature_groups[name]
            for group, params in fgroups.iteritems():
                if params is None:
                    self._container.applyFeature(group)
                else: # special case for haralick features
                    for param in params:
                        container.haralick_distance = param
                        container.applyFeature(group)

    def segementation(self, params):
        assert isinstance(params, dict)
        assert set(params.keys()) == set(self.cnames)

        # segment the master first
        cname = self._cnames[self._master_channel]
        image = self._image[:, :, self._master_channel]
        self._containers[cname] = self.threshold(image, *params[cname])
        label_image = self._container[cname].img_labels.toArray()

        for i, cname in enumerate(self.cnames):
            if i == self._master_channel:
                continue
            self._containers[name] = self.seededExpandedRegion(
                self.image[:, :, i], label_image, *params[name])

    def threshold(self, mean_radius, window_size, min_contrast,
                  remove_borderobjects, fill_holes):

        image = ccore.numpy_to_image(self.image, copy=True)
        image = ccore.disc_median(image, mean_radius)
        seg_image = ccore.window_average_threshold(
            image, window_size, min_contrast)

        if fill_holes:
            ccore.fill_holes(seg_image)

        return ccore.ImageMaskContainer(image, seg_image,
                                        remove_borderobjects)

    def seededExpandedRegion(self, label_image, srg_type, label_number,
                             region_statistics_array=0,
                             expansion_size=1,
                             sep_expansion_size=0):

        n_objects = label_image.max() + 1
        image = ccore.numpy_to_image(self.image, copy=True)
        limage = ccore.numpy_to_image(label_image, copy=True)

        img_labels = ccore.seeded_region_expansion(image, limage,
                                                   srg_type,
                                                   n_objects,
                                                   region_statistics_array,
                                                   expansion_size,
                                                   sep_expansion_size)

        return ccore.ImageMaskContainer(image, img_labels, False, True, True)
