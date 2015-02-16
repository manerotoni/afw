"""
guesser.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ("guessHdfType", )


from os.path import splitext
from cat.hdfio.cellh5reader import Ch5Reader
from cat.hdfio.trainingset import AtTrainingSetIO


def guessHdfType(filename):
    """Returns an instance of that class that implements the correct data model.

    The file mode is fixed according to the data model.
    -) cellh5 only reading -> mode 'r'
    -) training set reading/writing -> mode 'a'

    """

    _, ext = splitext(filename)
    if ext in Ch5Reader.EXTENSIONS:
        return Ch5Reader(filename, "a", cached=True)
    elif ext in AtTrainingSetIO.EXTENSIONS:
        return AtTrainingSetIO(filename, "a")
    else:
        raise IOError("filetype is unsupported")
