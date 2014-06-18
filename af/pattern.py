"""
pattern.py

Some design pattern collected
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

__all__ = ["Singleton", "QSingleton"]


from PyQt4.QtCore import pyqtWrapperType
import os


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
