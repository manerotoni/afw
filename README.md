CellAnnotationTool
--------------------

The CellAnnotationTool is an **interactive tool** for classifier training and validation. It presents the items (cells) as gallery to the user. A key feature is that the thumbnails are sorted by their similarity i.e. the user clicks on an item (or selects several items) and defines these items as representative examples of a certain class or cellular phenotype. The galleries are then sorted by e.g. cosine similarity relative to these examples. Since similar cells are grouped together the annotation of class labels is then rather simple. 

Annotation is performed by again selecting items and add these items to the class in the sidebar. Currently the tool supports the *One Class Support Vector Machine* for *inlier/outlier* separation and the *Support Vector Classifier* for the *multiclass problem*. 
In case of the support vector classifer the user has to setup a class definition (number of classes and class names)

###Data Import###

The tool reads cellh5/hdf5 files but can import also *.lsm and *.tif files directly using an import wizard.

###Installation###

Install the following depenencies:
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
