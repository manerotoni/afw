"""
debug.py

Collection of helper functions for debugging

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import time

def timing(func):

    def wrapper(*arg, **kw):
        """source: http://www.daniweb.com/code/snippet368.html"""
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        return (t2 - t1), res, func.__name__
    return wrapper
