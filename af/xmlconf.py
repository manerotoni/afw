"""
xmlconf.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from collections import namedtuple, OrderedDict
from lxml import etree

from af.segmentation.options import PrimaryParams
from af.segmentation.options import ExpansionParams
from af.segmentation.options import SRG_TYPE

def validate_tagname(name, reverse=False):
    if reverse:
        return name.replace("_", " ")
    else:
        return name.replace(" ", "_")


class XmlConf(object):

    PRIMARY = "primary_segmentation"
    SEGMENTATION = "segmentation"
    FEATUREGROUPS = "feature_groups"
    CONFIG = "config"


class XmlConfWriter(XmlConf):

    def __init__(self, segmentation, features):
        self.root = etree.Element(self.CONFIG)
        self.root.set(self.PRIMARY, validate_tagname(segmentation.keys()[0]))

        self._addElement(self.SEGMENTATION, segmentation)
        self._addElement(self.FEATUREGROUPS, features)

    def _addElement(self, name, dict_):
        for key, value in dict_.items():
            key = validate_tagname(key)
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

    def save(self, filename):
        with open(filename, "wb+") as fp:
            fp.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
            fp.write(self.toString())


class XmlConfReader(XmlConf):

    def __init__(self, filename):
        super(XmlConfReader, self).__init__()
        rparser = etree.XMLParser(remove_comments=True,
                                  remove_blank_text=True)
        self.root = etree.parse(filename, rparser).getroot()

    def element2NamedTuple(self, element):

        rparser = etree.XMLParser(remove_comments=True,
                                  remove_blank_text=True)
        root = etree.parse(self.filename, rparser).getroot()

    def _attrib2dict(self, attrib):
        evalattrib = dict()
        for key, value in attrib.iteritems():
            try:
                value = eval(value)
            except SyntaxError:
                # perhaps a list or tuple
                value = eval(",".join(value.split()))
            evalattrib[key] = value
        return evalattrib

    def primarySettings(self):
        primary = self.root.attrib[self.PRIMARY]
        settings = dict()

        # segmentation
        segm = self.root.xpath("%s/%s" %(primary, self.SEGMENTATION))[0]
        values = [eval(v) for v in segm.attrib.values()]
        settings[segm.tag] = PrimaryParams(*values)

        # feature groups
        fgrp = self.root.xpath("%s/%s" %(primary, self.FEATUREGROUPS))[0]
        settings[fgrp.tag] = self._attrib2dict(fgrp.attrib)
        return validate_tagname(primary, reverse=True), settings

    def expandedSettings(self, channel):

        channel = validate_tagname(channel)
        settings = dict()

        # segmentation
        try:
            segm = self.root.xpath("%s/%s" %(channel, self.SEGMENTATION))[0]
        except IndexError as e:
            raise ValueError("no settings for %s" %channel)


        values = list()
        for v in segm.attrib.values():
            if v in SRG_TYPE.keys():
                values.append(SRG_TYPE[v])
            else:
                values.append(eval(v))


        settings[segm.tag] = ExpansionParams(*values)

        # feature groups
        fgrp = self.root.xpath("%s/%s" %(channel, self.FEATUREGROUPS))[0]
        settings[fgrp.tag] = self._attrib2dict(fgrp.attrib)
        return settings
