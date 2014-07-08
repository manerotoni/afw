"""
xmlconf.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from collections import namedtuple
from lxml import etree


class XmlConf(object):

    def __init__(self, segmentation, features):
        self.root = etree.Element("config")


        self.root.set("primary_segmentation", segmentation.keys()[0])

        self._addElement("segmentation", segmentation)
        self._addElement("feature_groups", features)

    def _addElement(self, name, dict_):
        for key, value in dict_.items():
            key = key.replace(" ", "_")
            element = self.root.find(key)
            if element is None:
                element = etree.SubElement(self.root, key)

            if hasattr(value, "_asdict"):
                value = value._asdict()

            element.append(self._fromDict(name, value))

    def _val2xml(self, value):
        if isinstance(value, (tuple, list)):
            return " ".join([str(v) for v in value])
        else:
            return str(value)

    def _fromDict(self, name, dict_):
        element = etree.Element(name)

        for k, v in dict_.iteritems():
            element.set(k, self._val2xml(v))

        return element

    def toString(self):
        return etree.tostring(self.root, pretty_print=True)
