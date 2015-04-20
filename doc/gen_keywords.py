"""
gen_keywords.py
"""

__author__ = 'rudolf.hoefler@gmail.com'


import sys
import os


keywords = list()
lines = open(sys.argv[1]).readlines()
for line in lines:
    if "<a name=" in line:
        anchor = line.split("name=")[1].split('"')[1]
        print """<keyword name="XXX" ref="%s#%s"/>""" %(sys.argv[1], anchor)
