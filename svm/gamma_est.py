
def estimate_gamma_by_sv(X, nu):
    # X: training data matrix
    # nu is nu
    max_training_samples = 10000

    xx = []
    yy = []
    # check all gammas from 2^-16 to 2^2
    for gamma in [2**g for g in range(-16, 2)]:
        # learn OCSVM
        classifier = OneClassSVM(kernel='rbf', nu=nu, gamma=gamma)

        ## This you probably don't need (only if data matrix is more entries than max_training_samples
        #idx = range(X.shape[0])
        #numpy.random.seed(1)
        #numpy.random.shuffle(idx)

        #X = X[idx[:min(max_training_samples, X.shape[0])], :]

        # fit classifier
        classifier.fit(X)

        # support-vector fraction
        s_frac = (classifier.support_vectors_.shape[0] / float(len(X)) )
        print " SV fraction %.2g %.4g ==> %.1f%" %(nu, gamma, s_frac*100

        if s_frac > 0.99:
            break
        xx.append(numpy.log2(gamma))
        yy.append(s_frac)

    yy = numpy.array(yy)
    ind = numpy.argmax(numpy.diff(yy[yy < 1.67 * nu]))

    pylab.figure()
    pylab.plot(xx,yy,'y')
    pylab.plot(xx[ind], yy[ind], 'ro', markerfacecolor='none', markeredgecolor='r', lw=3)
    pylab.show()


    print ' best gamma at', xx[ind], 2**xx[ind], 'with SV frac', yy[ind]

    return 2**xx[ind]
