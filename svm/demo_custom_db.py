"""
demo_svm.py

Benchmark different out/inlier dectection methods

"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
sys.path.append("../")

import argparse
import numpy as np


from matplotlib import pyplot
import matplotlib.cm as cm
from sklearn import svm

from preprocessor import PreProcessor

def plot2d(traindata, testdata,
           nu=0.1, gamma=0.5, axes=None, limits=None,
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
                 s=120, lw=0, label="trainingset")

    axes.scatter(clf2d.support_vectors_[:, 0], clf2d.support_vectors_[:,1],
                 label="support_vectors", c="blue", s=100, marker="+")

    axes.scatter(testdata[:, 0][imask], testdata[:, 1][imask], label="inlier",
                 c='green', marker="o")
    axes.scatter(testdata[:, 0][omask], testdata[:, 1][omask], label="outlier",
                 c='red', marker="o")

    # axes.legend(frameon=True, fancybox=True)
    axes.set_title("nu=%.2g, gamma=%.2g" %(nu, gamma))

    return axes, clf2d

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

    import pdb; pdb.set_trace()

    axes.scatter(clf2d.support_vectors_[:, idx][:, 0],
                 clf2d.support_vectors_[:, idx][:,1],
                 label="support_vectors", c="blue", s=100, lw=1, marker="+")

    axes.scatter(ts[:, 0][imask], ts[:, 1][imask], label="inlier",
                 c='green', marker="o")
    axes.scatter(ts[:, 0][omask], ts[:, 1][omask], label="outlier",
                 c='red', marker="o")

    # axes.legend(frameon=True, fancybox=True)
    axes.set_title("nu=%.2g, gamma=%.2g" %(nu, gamma))

    return axes, clf2d


if __name__ == "__main__":

    parser = argparse.ArgumentParser(\
        description='Demo script for "inlier" detection benchmark')
    parser.add_argument("-t", "--training-data", dest="training_data",
                        help="csv file of the training set")
    parser.add_argument('-s', "--test-data", dest="test_data",
                        help='Csv file of the test data')

    args = parser.parse_args()

    pp = PreProcessor(args.training_data, args.test_data)
    idx = pp.index(["roisize","n2_avg"])

    nu = 0.01
    gamma = 0.5

    axes, clf = plot2d(pp.traindata[:, idx], pp.testdata[:, idx],  nu, gamma)
    # axes, clf = plot2d_combined(pp.traindata, pp.testdata, idx, nu, gamma)

    axes.set_xlim((-3, 6))
    axes.set_ylim((-1.8, 3))


    # fig.savefig("/Users/hoefler/assistant/volume.pdf")

    pyplot.show()
