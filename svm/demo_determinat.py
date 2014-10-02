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
import numpy.linalg as la
from sklearn import svm
import matplotlib.cm as cm


import matplotlib.pyplot as plt
from preprocessor import PreProcessor
from annot.mining import PCA

def volume(data, nu, gamma):
    """Return the volumen unter the decission function for the area inside
    the bordering contour.
    """

    clf2d = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    clf2d.fit(data)

    # plot 2d
    X, Y = np.meshgrid(np.linspace(-5, 5, 500), np.linspace(-5, 5, 500))
    # plot the line, the points, and the nearest vectors to the plane
    Z = clf2d.decision_function(np.c_[X.ravel(), Y.ravel()])
    Z = Z.reshape(X.shape)
    Z[Z<0] = 0.0
    # Z[Z>0] = 1.0

    dx = np.diff(X[0, :])[0]
    dy = np.diff(Y[:, 0])[0]
    return Z.sum()*dx*dy


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

    traindata = pp.traindata[:, idx]
    testdata = pp.testdata[:, idx]

    cov0 = np.cov(pp.traindata.T)
    corr0 = np.corrcoef(pp.traindata.T)
    det0 = la.det(corr0)
    fig = plt.figure()
    axes = fig.add_subplot(1,1,1)
    axes.matshow(cov0, cmap=cm.Greens)
    axes.set_title("covariance of training data")

    pca =  PCA(pp.traindata, minfrac=0.01)
    cov0pca = np.cov(pca.project(pp.traindata).T)
    corr0pca = np.corrcoef(pca.project(pp.traindata).T)
    det0pca = la.det(cov0pca)
    fig = plt.figure()
    axes = fig.add_subplot(1,1,1)
    axes.matshow(cov0pca, cmap=cm.Greens)
    axes.set_title("covariance of PCA training data")

    # print "rank:", np.rank(corr0)
    # print "det(pca)=%g" %(la.det(corr0))
    # print "det(pca)=%g" %(np.trace(corr0pca))

    # #pca =  PCA(pp.testdata)
    # cov1 = np.cov(pp.testdata.T)
    # fig = plt.figure()
    # axes = fig.add_subplot(1,1,1)
    # axes.matshow(cov1, cmap=cm.Greens)
    # axes.set_title("covariance of test data")

    # cov1_pca = np.cov(pca.project(pp.testdata).T)
    # fig = plt.figure()
    # axes = fig.add_subplot(1,1,1)
    # axes.matshow(cov1_pca, cmap=cm.Greens)
    # axes.set_title("covariance of PCA training data")



    plt.show()
