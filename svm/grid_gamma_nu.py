"""
grid_gamma_nu.py

grid plot of the one class svm parameters gamma and nu.
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
from plots import plot2d

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

    fig, axes = plt.subplots(5, 5, sharex=True, sharey=True,
                             **{"figsize": (25, 25)})

    nus= np.linspace(0.01, 0.9, 5)
    gammas = np.linspace(0.01, 0.9, 5)


    for i, nu in enumerate(nus):
        for j, gamma in enumerate(gammas):
            plot2d(pp.traindata[:, idx], pp.testdata[:, idx], nu, gamma,
                   axes[i][j], hide_axes=True)
            axes[i][j].set_xlim((-3.5, 5))
            axes[i][j].set_ylim((-1.8, 4))

    fig.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.99,
                        wspace=0.05, hspace=0.13)


    fig.savefig("/Users/hoefler/assistant/5x5.pdf")

    plt.show()
