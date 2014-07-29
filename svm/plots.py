"""
plots.py
"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'


import numpy as np
from matplotlib import pyplot
import matplotlib.cm as cm
from sklearn import svm


def plot2d(traindata, testdata, nu=0.1, gamma=0.5, axes=None, limits=None,
           hide_axes=False):

    # 2d model for contourf
    clf2d = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    clf2d.fit(traindata)
    pred = clf2d.predict(testdata)

    xlim, ylim = np.array([(testdata[:, 0].min(), testdata[:, 0].max()),
                           (testdata[:, 1].min(), testdata[:, 1].max())])

    # plot 2d
    X, Y = np.meshgrid(np.linspace(xlim[0], xlim[1], 150),
                       np.linspace(ylim[0], ylim[1], 150))
    # plot the line, the points, and the nearest vectors to the plane
    Z = clf2d.decision_function(np.c_[X.ravel(), Y.ravel()])
    Z = Z.reshape(X.shape)

    if axes is None:
        fig = pyplot.figure()
        axes = fig.add_subplot(1, 1 ,1)


    axes.contourf(X, Y, Z, cmap=cm.Blues_r)
    axes.contour(X, Y, Z, colors='orange')

    # scatter plots
    imask = (pred == 1)
    omask = (pred == -1)
    axes.scatter(traindata[:, 0], traindata[:, 1], c='yellow', marker="o",
                 s=100, lw=0, label="trainingset")
    axes.scatter(testdata[:, 0][imask], testdata[:, 1][imask], label="inlier",
                 c='green', marker="o")
    axes.scatter(testdata[:, 0][omask], testdata[:, 1][omask], label="outlier",
                 c='red', marker="o")

    # axes.legend(frameon=True, fancybox=True)
    axes.set_title("nu=%.2g, gamma=%.2g" %(nu, gamma))

    if limits is not None:
        axes.set_xlim(limits[0])
        axes.set_ylim(limits[1])

    if hide_axes:
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

    return axes


def plot2d_combined(traindata, testdata, idx, nu=0.1, gamma=0.5, axes=None):

    tr = traindata[:, idx]
    ts = testdata[:, idx]

    # 2d model for contourf
    clf2d = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    clf2d.fit(tr)
    pred = clf2d.predict(ts)

    xlim, ylim = np.array([(ts[:, 0].min(), ts[:, 0].max()),
                           (ts[:, 1].min(), ts[:, 1].max())])

    # plot 2d
    X, Y = np.meshgrid(np.linspace(xlim[0], xlim[1], 150),
                       np.linspace(ylim[0], ylim[1], 150))
    # plot the line, the points, and the nearest vectors to the plane
    Z = clf2d.decision_function(np.c_[X.ravel(), Y.ravel()])
    Z = Z.reshape(X.shape)

    if axes is None:
        fig = pyplot.figure()
        axes = fig.add_subplot(1, 1 ,1)

    axes.contourf(X, Y, Z, cmap=cm.Blues_r)
    axes.contour(X, Y, Z, colors='orange')

    # 2d model for contourf
    clf2d = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    clf2d.fit(traindata)
    pred = clf2d.predict(testdata)

    # scatter plots
    imask = (pred == 1)
    omask = (pred == -1)

    axes.scatter(tr[:, 0], tr[:, 1], c='yellow', marker="o",
                 s=100, lw=0, label="trainingset")
    axes.scatter(ts[:, 0][imask], ts[:, 1][imask], label="inlier",
                 c='green', marker="o")
    axes.scatter(ts[:, 0][omask], ts[:, 1][omask], label="outlier",
                 c='red', marker="o")

    # axes.legend(frameon=True, fancybox=True)
    axes.set_title("nu=%.2g, gamma=%.2g" %(nu, gamma))

    return axes
