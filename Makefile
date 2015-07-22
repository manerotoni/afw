# Copyright (c) 2015
# Gerlich Lab, IMBA Vienna, Austria
# rudolf.hoefler@gmail.com
# 17/07/2015
# This software can be distribute under the term of the GPL

VERSION = 0.6.0
ARCH=$$(uname -m)
APPNAME = CellAnnotator
TMPNAME = CellAnnotator.dmg
DMGNAME = CellAnnotator_$(VERSION)_$(ARCH).dmg
VOLNAME = $(APPNAME)-$(VERSION)

all: dmg

osx:
	python setup_mac.py py2app

dmg: osx
	hdiutil create -srcfolder dist/$(APPNAME).app \
	-volname $(VOLNAME) -fs HFS+ -format UDRW $(TMPNAME)
	hdiutil attach -readwrite -noverify -noautoopen $(TMPNAME)
	ln -s /Applications /Volumes/$(VOLNAME)/Applications
	hdiutil detach /Volumes/$(VOLNAME)
	hdiutil convert $(TMPNAME) -format UDZO -imagekey zlib-level=6 -o $(DMGNAME)
	rm $(TMPNAME)
clean:
	rm -rfv build dist
	rm -fv *.dmg
	rm -fv *.*~

inplace:
	python setup.py build_rcc
	python setup.py build_help
