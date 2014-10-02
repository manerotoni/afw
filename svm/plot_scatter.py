
import sys
sys.path.append("../")


from annot.mining import ZScore

import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm


def filter_mask(data):
    """Retrun a mask where columns with zero variance and nans are False."""
    return np.invert(np.isnan(data.sum(axis=0)))*(data.std(axis=0) > 0.0)


# rosize = 236, intesity=222, std=223 (-1 because one columw will be removed)
# features = [235, 221] # one column is remove later
# tset = np.loadtxt("./trainingset.csv", delimiter=",")
# mixed = np.loadtxt("./all.csv", delimiter=",")

# rosize = 236, intesity=222, std=223 (-1 because one columw will be removed)
features = [17, 6]
tset = np.loadtxt("data/reduced_featuresset/metaphase.csv", delimiter=",")
mixed = np.loadtxt("data/reduced_featuresset/all.csv", delimiter=",")


mask = filter_mask(tset)
tset = tset[:, mask]
mixed = mixed[:, mask]

zs = ZScore(tset)
tset = zs.normalize(tset)
mixed = zs.normalize(mixed)

# fit the model
clf = svm.OneClassSVM(nu=0.001, kernel="rbf", gamma=0.01)
clf.fit(tset)


ytset = clf.predict(tset)
ymixed = clf.predict(mixed)

n_error_train = ytset[ytset == -1].size
n_error_outliers = ymixed[ymixed == 1].size

xmin = mixed[:, 0].min()-1
xmax = mixed[:, 0].max()+1
ymin = mixed[:, 1].max()-1
ymax = mixed[:, 1].max()+1


X, Y = np.meshgrid(np.linspace(xmin, xmax, 500),
                   np.linspace(ymin, ymax, 500))


# plot the line, the points, and the nearest vectors to the plane
# Z = clf.decisdion_function(np.c_[X.ravel(), Y.ravel()])
# Z = Z.reshape(X.shape)

tset = tset[:, features]
mixed = mixed[:, features]


imask = ymixed == 1
omask = ymixed == -1

plt.figure(figsize=(12, 8))

b1 = plt.scatter(tset[:, 0], tset[:, 1], c='blue', marker="o", s=100, lw=0,
                 label="trainingset", alpha=0.5)
c = plt.scatter(mixed[:, 0][imask], mixed[:, 1][imask], label="inlier",
                c='green', marker="o")
c = plt.scatter(mixed[:, 0][omask], mixed[:, 1][omask], label="outlier",
                c='red', marker="o")


plt.title("In vs. Outlier")
plt.xlabel("size")
plt.ylabel("intesity")

plt.ylim((-2, 4))
plt.xlim((-4, 3))

plt.legend(frameon=False)
plt.show()
