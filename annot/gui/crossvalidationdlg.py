"""
crossvalidation.py

Popup dialog to perform cross validation and gridsearch.

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


from os.path import splitext
import numpy as np
from multiprocessing import cpu_count
from matplotlib.figure import Figure
from matplotlib import cm

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import uic
from PyQt4.QtGui import QApplication, QCursor

from sklearn import svm
from sklearn.svm import SVC
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedKFold

from annot.qmpl import QFigureWidget
from annot.gui.sidebar.sidebar import NoSampleError


class CrossValidationDialog(QtGui.QWidget):

    requestDataUpdate = QtCore.pyqtSignal()
    gridSearchFinished = QtCore.pyqtSignal()
    crossValidationFinished = QtCore.pyqtSignal()

    def __init__(self, parent, classifier, *args, **kw):
        super(CrossValidationDialog, self).__init__(parent=parent, *args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)
        self.setWindowFlags(Qt.Window)

        self.classifier = classifier
        self._tabs = dict()

        self.applyBtn.clicked.connect(self.onApplyBtn)
        self.okBtn.clicked.connect(self.onOkBtn)

        self.crossValBtn.clicked.connect(self.onCrossValiation)
        self.gridSearchBtn.clicked.connect(self.onGridSearch)
        self.gridSearchFinished.connect(self.crossValidation)
        self.gridSearchFinished.connect(self.onApplyBtn)
        self.gridSearchFinished.connect(parent.predictionInvalid)
        self.requestDataUpdate.connect(self.updateData)

        self.features = None
        self.labels =  None

    def onApplyBtn(self):
        self.classifier.setParameters(self.parameters)

    def onOkBtn(self):
        self.classifier.setParameters(self.parameters)
        self.hide()

    def updateData(self):
        """Update the current feature table (and the corresponding labels)
        from the model that belongs to the classifier."""

        try:
            features = self.parent().filterFeatures(
                self.parent().model.features)
        except NoSampleError:
            return
        preprocessor = self.classifier.setupPreProcessor(features)
        features = self.classifier.normalize(features)

        # setup gamma only the first time
        if self.features is None:
            self.gamma.setValue(1./features.shape[0])

        self.features =  features
        self.labels =  self.parent().model.labels

    @property
    def parameters(self):
        return {"gamma": self.gamma.value(),
                "C": self.regConst.value()}

    def showMessage(self, message=''):
        self.output.append(message)

    def addFigure(self, title, figure):

        # no dublicate tabs
        if self._tabs.has_key(title):
            idx = self._tabs[title]
            self.tabWidget.widget(idx).close()
            self.tabWidget.removeTab(idx)

        qfw = QFigureWidget(figure, self)
        idx = self.tabWidget.addTab(qfw, title)
        self._tabs[title] = idx
        self.tabWidget.setCurrentWidget(qfw)
        qfw.show()

    @property
    def kfold(self):
        return int(self.fold.currentText())

    def onCrossValiation(self):
        self.requestDataUpdate.emit()
        if self.features is None:
            return
        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.crossValidation()
        finally:
            QApplication.restoreOverrideCursor()

    def crossValidation(self):
        scoring_methods = ("accuracy", "f1", "precision", "recall")
        clf = svm.SVC(kernel="rbf", C=self.regConst.value(),
                      gamma=self.gamma.value())


        self.showMessage("metric\tmean std".upper())
        for sm in scoring_methods:
            scores = cross_validation.cross_val_score(
                clf, self.features, self.labels, cv=self.kfold, scoring=sm)
            txt = "%s:\t %0.2f +/-%0.2f" %(sm.title(), scores.mean(), scores.std())
            self.showMessage(txt)
        self.showMessage()

    def onGridSearch(self):
        self.requestDataUpdate.emit()
        if self.features is None:
            return
        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.gridSearch()
        finally:
            QApplication.restoreOverrideCursor()

    def gridSearch(self):

        self.showMessage('Grid search using %d-fold cross_validation'
                         %self.kfold)
        C = np.logspace(-6, 6, self.grid_C.value())
        gamma = np.logspace(-6, 6, self.grid_gamma.value())
        param_grid = dict(gamma=gamma, C=C)

        cv = StratifiedKFold(y=self.labels, n_folds=self.kfold)
        grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv,
                            n_jobs=cpu_count()-1)
        grid.fit(self.features, self.labels)
        est = grid.best_estimator_

        self.showMessage("optimal parameters:")
        self.showMessage("C: %g, gamma: %g" %(est.C, est.gamma))
        self.showMessage()

        scores = np.array([s.mean_validation_score for s in grid.grid_scores_])
        S = scores.reshape((C.size, gamma.size))

        X, Y = np.meshgrid(gamma, C)

        self.gamma.setValue(est.gamma)
        self.regConst.setValue(est.C)
        self.plotGridSearch(X, Y, S, est.gamma, est.C)
        self.gridSearchFinished.emit()

    def plotGridSearch(self, X, Y, S, gamma, C):

        fig = Figure()
        ax = fig.add_subplot(111)

        ax.contour(X, Y, S)
        pc = ax.pcolormesh(X, Y, S, shading='gouraud', cmap=cm.coolwarm)
        fig.colorbar(pc)
        ax.axvline(gamma, linewidth=1, color='yellow')
        ax.axhline(C, linewidth=1, color='yellow')

        ax.set_xlabel('gamma')
        ax.set_ylabel('C')
        ax.set_title('gamma=%g, C=%g' %(gamma, C))
        ax.loglog()
        self.addFigure('Grid Search', fig)
