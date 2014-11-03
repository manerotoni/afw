
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

class ValidationDialog(QtGui.QDialog):

    gridSearchFinished = QtCore.pyqtSignal()
    crossValidationFinished = QtCore.pyqtSignal()

    def __init__(self, features, labels, *args, **kw):
        super(ValidationDialog, self).__init__(*args, **kw)
        uic.loadUi(splitext(__file__)[0]+'.ui', self)

        self.crossValBtn.clicked.connect(self.onCrossValiation)
        self.gridSearchBtn.clicked.connect(self.onGridSearch)
        self.gridSearchFinished.connect(self.crossValidation)

        self.gamma.setValue(1./features.shape[0])

        self.features =  features
        self.labels =  labels

    def showMessage(self, message=''):
        self.output.append(message)

    def addFigure(self, title, figure):
        qfw = QFigureWidget(figure, self)
        self.tabWidget.addTab(qfw, title)
        self.tabWidget.setCurrentWidget(qfw)
        qfw.show()

    @property
    def kfold(self):
        return int(self.fold.currentText())

    def onCrossValiation(self):
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
        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            self.gridSearch()
        finally:
            QApplication.restoreOverrideCursor()

    def gridSearch(self):

        self.showMessage('Grid search using %d-fold cross_validation'
                         %self.kfold)
        C = np.logspace(-3, 3, self.grid_C.value())
        gamma = np.logspace(-5, 2, self.grid_gamma.value())
        param_grid = dict(gamma=gamma, C=C)

        cv = StratifiedKFold(y=labels, n_folds=self.kfold)
        grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv,
                            n_jobs=cpu_count()-1)
        grid.fit(self.features, self.labels)
        est = grid.best_estimator_

        self.showMessage("optimal parameters:")
        self.showMessage("C: %g, gamma: %g" %(est.C, est.gamma))
        self.showMessage()

        scores = grid.grid_scores_
        scores = np.array([s.mean_validation_score for s in scores])
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



if __name__ == "__main__":
    import sys

    f1 = "cross_validation/features.csv"
    f2 = "cross_validation/labels.csv"
    features = np.loadtxt(f1)
    labels = np.loadtxt(f2)

    app = QtGui.QApplication(sys.argv)


    vd = ValidationDialog(features, labels)
    vd.show()
    app.exec_()
