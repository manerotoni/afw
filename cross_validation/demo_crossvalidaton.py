
import numpy as np
from sklearn import svm
from sklearn import cross_validation
from sklearn.cross_validation import StratifiedKFold

if __name__ == "__main__":
    Y= np.loadtxt("labels.csv")
    X = np.loadtxt("features.csv")


    Xtrain, Xtest, ytrain, ytest = cross_validation.train_test_split(
        X, Y, test_size=0.1, random_state=0)

    # classifier with default parameters C=1, gamma=1/nsamples
    clf = svm.SVC(kernel="rbf")
    # clf.fit(Xtrain, ytrain)
    # print clf.score(Xtest, ytest)

    scores = cross_validation.cross_val_score(clf, X, Y, cv=5)
    scores = cross_validation.cross_val_score(clf, X, Y, cv=5)

    print("Accurracy: %0.2f (+/- %0.2f)" %(scores.mean(), scores.std()*2))



    import pdb; pdb.set_trace()
