

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap

from sklearn.svm import SVC
from sklearn.cross_validation import StratifiedKFold

from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV



labels = np.loadtxt("labels.csv")
features = np.loadtxt("features.csv")


C = np.logspace(-3, 3, 10)
gamma = np.logspace(-5, 2, 10)
param_grid = dict(gamma=gamma, C=C)


scoring_methods = ("accuracy", "f1", "precision", "recall")
#scoring_methods = ("accuracy", )


cv = StratifiedKFold(y=labels, n_folds=5)
grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
grid.fit(features, labels)
est = grid.best_estimator_

print "C: %g, gamma: %g" %(est.C, est.gamma)

scores = grid.grid_scores_
scores = np.array([s.mean_validation_score for s in scores])
S = scores.reshape((C.size, gamma.size))


# classifier with default parameters C=1, gamma=1/nsamples
clf = SVC(kernel="rbf", C=est.C, gamma=est.gamma)
for sm in scoring_methods:
    cv = StratifiedKFold(y=labels, n_folds=5)
    scores = cross_validation.cross_val_score(clf, features, labels, cv=cv, scoring=sm)
    print("%s: %0.2f (+/- %0.2f)" %(sm, scores.mean(), scores.std()*2))



X, Y = np.meshgrid(gamma, C)
plt.figure()
plt.pcolormesh(X, Y, S, shading='gouraud', cmap=cm.coolwarm)
plt.colorbar()
plt.axvline(est.gamma, linewidth=1, color='k')
plt.axhline(est.C, linewidth=1, color='k')
# plt.scatter([est.gamma], [est.C], marker="o", s=80, color='#FFFF00')

plt.xlabel('gamma')
plt.ylabel('C')
plt.loglog()
plt.show()
