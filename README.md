Cell Annotation Tool
--------------------

Cell Annotation Tool is an **interactive tool** for classifier training and validation. It presents the items (cells) as gallery image. A key feature is that the gallery images are sorted by their similarity i.e. the user clicks on an item (or selects several items) and defines these items as representative examples of a certain class. The galleries are then sorted by cosine similarity relative to these examples. Since similar cells are grouped together the annotation of class labels is then rather simple. 
Annotation is performed by again selecting items (mark them) and add those items to the class in the sidebar. Currently the tools supports the **One Class Support Vector Machine** for inlier/outlier separation and the **Support Vector Classifier** for the multiclass problem. 
In case of the support vector classifer the user has to setup a class definition (number of classes and class names)

###Data Import###

The tool reads cellh5/hdf5 files but can import also *.lsm files directly using an import wizard. The wizard will be extended to read tiff files in future versions.

###Installation###

The Cell Annotation tool is an PyQt4 application depends on the:
* [cellcognition framework](https://github.com/CellCognition/cecog.git)
* [vigranumpy](http://ukoethe.github.io/vigra/doc-release/vigranumpy/index.html)
* [sklearn](http://scikit-learn.org/)
* [PyQt4](http://www.riverbankcomputing.com/software/pyqt/download) 
* [pylsm](https://launchpad.net/pylsm)
* [numpy](http://www.numpy.org/)
* [scipy](http://www.scipy.org/)
* [matplotlib](http://matplotlib.org/)


```
git clone https://github.com/rhoef/afw.git
cd afw
python setup.py install
```
or build a Windows installer package
```
python setup.py bdist_wininst
```
