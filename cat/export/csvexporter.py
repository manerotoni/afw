"""
csvexporter.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


__all__ = ('CsvExporter', 'StatsExporter')

import csv
from collections import defaultdict

class CsvExporter(object):

    def __init__(self, filename, items, features):
        self._features = features
        self._filename = filename
        self._items = items

    def save(self):

        header = ['class', 'class_label', 'treatment']
        header.extend(self._features.values())

        with open(self._filename, 'wb') as fp:
            writer = csv.writer(fp, delimiter=',',)
            writer.writerow(header)

            for item in self._items:
                line = [item.class_.name, item.class_.label, item.treatment]
                line.extend(item.features[self._features.keys()].tolist())
                writer.writerow(line)


class StatsExporter(object):

    def __init__(self, filename, items, features):
        self._features = features
        self._filename = filename
        self._items = items

    def save(self):

        counter = lambda: defaultdict(lambda: 0)
        treatments = defaultdict(counter)
        classes = dict()

        for item in self._items:
            treatments[item.treatment][item.class_.name] += 1
            classes[item.class_.label] = item.class_.name

        header = ['Treatment'] + classes.values()

        with open(self._filename, 'wb') as fp:
            writer = csv.DictWriter(fp, delimiter=',', fieldnames=header)
            writer.writeheader()

            for treatment, counts in treatments.iteritems():
                line = dict([('Treatment', treatment)])
                line.update(counts)
                writer.writerow(line)
