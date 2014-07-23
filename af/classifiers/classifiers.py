"""
classifier.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("Classifier", )

from af.pattern import Factory


class Classifier(object):
    """Parent factory for all classifier classes"""

    __metaclass__ = Factory

    @classmethod
    def classifiers(cls):
        return cls._classes.keys()


class OneClassSvm(Classifier):
    """Class for training and parameter tuning of a one class svm."""

    pass
