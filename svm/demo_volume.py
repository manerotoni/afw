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

from sklearn import svm
import matplotlib.cm as cm


import matplotlib.pyplot as plt
from preprocessor import PreProcessor

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

    nus = np.linspace(0.01, 0.9, 100)
    gammas = np.linspace(0.01, 0.9, 100)
    NU, GAMMA = np.meshgrid(nus, gammas)
    VOL = np.empty(NU.shape)

    for i, nu in enumerate(nus):
        for j, gamma in enumerate(gammas):
            VOL[i, j] = \
                volume(pp.traindata[:, idx], nu, gamma)

    fig = plt.figure()
    axes = fig.add_subplot(1,1,1)
    axes.contourf(NU, GAMMA, VOL)
    axes.set_title("Volum(nu, gamma)")
    axes.set_xlabel("gamma")
    axes.set_ylabel("nu")

    # fig.savefig("/Users/hoefler/assistant/volume.pdf")

    plt.show()
