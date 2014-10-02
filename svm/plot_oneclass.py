
import sys
sys.path.append("../")


from annot.mining import ZScore, PCA

import numpy as np
import matplotlib.pyplot as plt
from sklearn import svm


def filter_mask(data):
    """Retrun a mask where columns with zero variance and nans are False."""
    return np.invert(np.isnan(data.sum(axis=0)))*(data.std(axis=0) > 0.0)


# rosize = 236, intesity=222, std=223 (-1 because one columw will be removed)
features = [17, 6]
tset = np.loadtxt("data/reduced_featuresset/metaphase.csv", delimiter=",")[:, features]
#outliers = np.loadtxt("./outliers.csv", delimiter=",")[:, features]
mixed = np.loadtxt("data/reduced_featuresset/all.csv", delimiter=",")[:, features]

# import pdb; pdb.set_trace()
# # filter out columns that contain nan's and have zero variance
mask = filter_mask(tset)
tset = tset[:, mask]
#outliers = outliers[:, mask]
mixed = mixed[:, mask]

# all_data = np.vstack((tset, outliers, mixed))
# ndgrid = meshgrid_nd(all_data)

zs = ZScore(tset)
tset = zs.normalize(tset)
#outliers = zs.normalize(outliers)
mixed = zs.normalize(mixed)


# fit the model
clf = svm.OneClassSVM(nu=0.01, kernel="rbf", gamma=0.5)
clf.fit(tset)

ytset = clf.predict(tset)
#youtliers = clf.predict(outliers)
ymixed = clf.predict(mixed)

n_error_train = ytset[ytset == -1].size
#n_error_test = youtliers[youtliers == -1].size
n_error_outliers = ymixed[ymixed == 1].size


xmin = mixed[:,0].min()-1
xmax = mixed[:,0].max()+1
ymin = mixed[:,1].min()-1
ymax = mixed[:,1].max()+1

plt.figure(figsize=(12, 8))
X, Y = np.meshgrid(np.linspace(xmin, xmax, 500),
                   np.linspace(ymin, ymax, 500))


# plot the line, the points, and the nearest vectors to the plane
Z = clf.decision_function(np.c_[X.ravel(), Y.ravel()])
Z = Z.reshape(X.shape)

plt.contourf(X, Y, Z, levels=np.linspace(Z.min(), 0, 7), cmap=plt.cm.Blues_r)
a = plt.contour(X, Y, Z, levels=[0], linewidths=1, ls="dashed", colors='red')
plt.contourf(X, Y, Z, levels=[0, Z.max()], colors='orange')

imask = ymixed == 1
omask = ymixed == -1


trn = plt.scatter(tset[:, 0], tset[:, 1], c='yellow', marker="o", s=100, lw=0,
                 label="trainingset")
inl = plt.scatter(mixed[:, 0][imask], mixed[:, 1][imask], label="inlier",
                c='green', marker="o")
out = plt.scatter(mixed[:, 0][omask], mixed[:, 1][omask], label="outlier",
                c='red', marker="o")

plt.legend([a.collections[0], trn, inl, out],
           ["learned frontier", "training observations",
            "inliers", "outliers"], frameon=False, loc=2)


plt.xlabel("size (norm.)")
plt.ylabel("intesity (norm.)")


plt.ylim((-2, 4))
plt.xlim((-4, 3))
plt.show()
