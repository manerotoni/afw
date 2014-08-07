"""
pattern.py

Some design pattern collected.
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ["Singleton", "QSingleton", "Factory"]


from PyQt4.QtCore import pyqtWrapperType


class Singleton(type):
    """Process save Singleton to get os.fork() working."""

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(cls, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):

        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instance


class QSingleton(pyqtWrapperType):
    """PyQt implementation of the singleton pattern to avoid the
    metaclass conflict.
    """

    def __init__(cls, name, bases, dict):
        super(QSingleton, cls).__init__(cls, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(QSingleton, cls).__call__(*args, **kwargs)
        return cls._instance


class Factory(type):
    """Meta class to implement the factory design pattern"""

    def __init__(cls, name, bases, dct):

        if not hasattr(cls, "_classes"):
            setattr(cls , "_classes", {})
        elif hasattr(cls, "_classes"):
            bases[0]._classes[name] = cls
            setattr(bases[0], name, name) # perhaps an int?
        return type.__init__(cls, name, bases, dct)

    def __call__(cls, klass=None, *args, **kw):

        if klass in cls._classes.keys():
            return cls._classes[klass](*args, **kw)
        elif klass is None:
            return type.__call__(cls, *args, **kw)
        elif cls in cls._classes.values():
            allargs = (klass, ) + args
            return type.__call__(cls, *allargs, **kw)
