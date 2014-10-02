"""
postinstall.py

Create a shortcut in the start menu after installation.
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import os
import sys

def mkshortcut(target, description, link_file, *args,**kw):
    """make a shortcut if it doesn't exist, and register its creation"""
    create_shortcut(target, description, link_file,*args,**kw)
    file_created(link_file)

def install():
    pythonw = os.path.join(sys.prefix, 'pythonw.exe')
    start_menu = get_special_folder_path('CSIDL_COMMON_PROGRAMS')

   # create directory in the start menu
    if not os.path.isdir(start_menu):
        os.mkdir(start_menu)
        directory_created(start_menu)

    link = os.path.join(start_menu, 'AnnotationTool.lnk')
    command = os.path.join(sys.prefix, 'Scripts', 'AnnotationTool.py')
    icon = os.path.join(sys.prefix, 'share', 'AnnotationTool', 'annotationtool.ico')
    workdir = "%HOMEDRIVE%%HOMEPATH%"
    mkshortcut(pythonw, 'AnnotationTool', link, command, workdir, icon)

def remove():
    pass

if sys.argv[1] == '-install':
    try:
        install()
    except Exception as e:
        fp = open(os.path.join(os.path.expanduser("~"),
                               "AnnotationToolInstallError.txt"), 'a')
        fp.write(e.message)
        raise
else:
    remove()
