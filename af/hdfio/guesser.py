"""
guesser.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("guessHdfType", )


from os.path import splitext
from af.hdfio import Ch5Reader, HdfTrainingSetReader


def guessHdfType(filename, *args, **kw):
    """Returns an instance of that class that implements the
    correct data model.
    """

    _, ext = splitext(filename)
    if ext in Ch5Reader.EXTENSIONS:
        return Ch5Reader(filename, "r", cached=True)
    elif ext in HdfTrainingSetReader.EXTENSIONS:
        return HdfTrainingSetReader(filename, "r")
    else:
        raise IOError("filetype is unsupported")
