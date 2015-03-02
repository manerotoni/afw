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
from matplotlib.ticker import FixedLocator

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import uic
from PyQt4.QtGui import QApplication, QCursor, QMessageBox

from sklearn import svm
from sklearn.svm import SVC
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedKFold

from cat.qmpl import QFigureWidget
from cat.gui.sidebar.sidebar import NoSampleError

def _font_color(value):
    """Helper function for matrix plot"""
    if value < 0.4:
        return "black"
    else:
        return "white"

def _font_size(value):
    """Helper function for matrix plot"""
    if value <= 3:
        return 30
    elif 3 < value < 9:
        return 15
    else:
        return 10


class CrossValidationDialog(QtGui.QWidget):

    requestDataUpdate = QtCore.pyqtSignal()
    gridSearchFinished = QtCore.pyqtSignal()
    crossValidationFinished = QtCore.pyqtSignal()

    ScoringMethods = ("accuracy", "f1", "precision", "recall")

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
        self.confusion_matrix = None

    def raise_(self):
        self.onGridSearch()
        super(CrossValidationDialog, self).raise_()

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

    def classifierIsValidated(self):
        return self.confusion_matrix is not None

    @property
    def parameters(self):
        return {"gamma": self.gamma.value(),
                "C": self.regConst.value()}

    def showMessage(self, message=''):
        self.output.append(message)

    def addFigure(self, title, figure):

        qfw = QFigureWidget(figure, self)
        qfw.hideToolbar()

        # no dublicate tabs
        if self._tabs.has_key(title):
            idx = self._tabs[title]
            self.tabWidget.widget(idx).close()
            self.tabWidget.removeTab(idx)
            self.tabWidget.insertTab(idx, qfw, title)
        else:
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

        clf = svm.SVC(kernel="rbf", C=self.regConst.value(),
                      gamma=self.gamma.value())


        self.showMessage("metric\tmean std".upper())
        for sm in self.ScoringMethods:
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
        except Exception as e:
            QMessageBox.warning(self, "Warning", str(e))
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

        predictions = est.predict(self.features)
        confmat = confusion_matrix(self.labels, predictions)
        self.plotConfusionMatrix(confmat)
        self.confusion_matrix = confmat
        self.gridSearchFinished.emit()

    def plotGridSearch(self, X, Y, S, gamma, C):

        fig = Figure(facecolor="white", tight_layout=True)
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


    def plotConfusionMatrix(self, confmat):

        confmat_norm = confmat.astype(float)/confmat.sum(axis=0)

        fig = Figure(facecolor="white", tight_layout=True)
        ax = fig.add_subplot(111)
        ax.matshow(confmat_norm, cmap=cm.Blues)

        classes = self.parent().model.currentClasses()
        names = [v.name for v in classes.values()]

        ax.xaxis.set_major_locator(FixedLocator(range(len(names))))
        ax.set_xticklabels(names, rotation=45, size=10)

        ax.yaxis.set_major_locator(FixedLocator(range(len(names))))
        ax.set_yticklabels(names, rotation=45, size=10)

        ax.set_xlabel("Predictions", fontsize=14)
        ax.set_ylabel("Annotations", fontsize=14)
        fig.subplots_adjust(top=0.85)

        size = _font_size(confmat.shape[0])
        for i, items in enumerate(confmat):
            for j, item in enumerate(items):
                color = _font_color(confmat_norm[j, i])
                ax.text(i, j, str(item), size=size, color=color,
                        va="center", ha="center")

        self.addFigure('Confusion Matrix', fig)
