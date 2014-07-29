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

import matplotlib.pyplot as plt
from preprocessor import PreProcessor
from plots import plot2d_combined
from knn import dist_knn

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
    gamma = dist_knn(pp.traindata, 10)
    print "mean dist", gamma
    # import pdb; pdb.set_trace()

    for i, nu in enumerate(nus):
        for j, gamma in enumerate(gammas):
            ax = axes[i][j]
            plot2d_combined(pp.traindata, pp.testdata, idx,  nu, gamma, ax)

            # # limits and axes
            # ax.set_xlim((-3.5, 5))
            # ax.set_ylim((-1.8, 4))
            # ax.get_xaxis().set_visible(False)
            # ax.get_yaxis().set_visible(False)

    fig.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.99,
                        wspace=0.05, hspace=0.13)

    fig.savefig("/Users/hoefler/assistant/grid_combined.pdf")

    plt.show()
