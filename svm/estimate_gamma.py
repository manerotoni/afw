"""
estimate_gamma.py


"""

__author__ = 'rudolf.hoefler@gmail.com'
__licence__ = 'GPL'

import sys
sys.path.append("../")

import argparse
import numpy as np
from sklearn import svm

import matplotlib.pyplot as plt
from preprocessor import PreProcessor
from scipy.optimize import leastsq


def estimate_gamma(testdata, nu, range_=(-16, 2), verbose=False):

    nsamples = testdata.shape[0]

    gammas = list()
    fractions = list()

    # check all gammas from 2^-16 to 2^2
    for gamma in 2**np.linspace(-16, 2, 100):
        clf = svm.OneClassSVM(kernel='rbf', nu=nu, gamma=gamma)
        clf.fit(testdata)

        s_frac = clf.support_.size/float(nsamples)

        if verbose:
            print " SV fraction %.2g %4g ==> %.1f %%" %(nu, gamma, s_frac*100)

        if s_frac > 0.80:
            break
        gammas.append(gamma)
        fractions.append(s_frac)

    return np.array(gammas), np.array(fractions)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(\
        description='Demo script for "inlier" detection benchmark')
    parser.add_argument("-t", "--training-data", dest="training_data",
                        help="csv file of the training set")
    parser.add_argument('-s', "--test-data", dest="test_data",
                        help='Csv file of the test data')

    args = parser.parse_args()


    pp = PreProcessor(args.training_data, args.test_data)

    # idx = pp.index(["roisize","n2_avg"])

    nu = 0.01
    x, y = estimate_gamma(pp.traindata, nu)

    idx = y[y <= 0.25].size - 1
    print ' best gamma:', x[idx], 'with SV frac', y[idx]

    fig =  plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x, y, 'ro', label='estimate')

    # ax.semilogx()
    ax.grid()
    # ax.legend(frameon=False)
    plt.show()
