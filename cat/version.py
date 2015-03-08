"""
version.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


MAJOR = 0
MINOR = 4

organisation = "IMBA"
appname = "CellAnnotator"
version = "%s.%s%s" %(MAJOR, MINOR, "-alpha")
appstr = '%s-%s' %(appname, version)

information = ('<p style="font-size:xx-large;color:white"><b>%s %s</b></p><br>'
               '<p style="line-height:25px;font-size:x-large;color:white">'
               'Copyright (c) 2014<br>'
               'Gerlich LAB - IMBA<br>'
               'Vienna Biocenter Campus</p>'
               '<p style="color:white">'
               'Author: rudolf.hoefler@gmail.com<br>'
               'License: GNU General Public License v3<br>'
               '<a href=http://www.gnu.org/copyleft/gpl.html>'
               'http://www.gnu.org/copyleft/gpl.html</a><br>'
               %(appname, version))
