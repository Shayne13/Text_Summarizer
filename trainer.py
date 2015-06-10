import itertools
import random
import time
import pickle
import numpy as np
from operator import itemgetter
from collections import Counter
from itertools import izip
import scipy
# import scipy.spatial.distance
from numpy.linalg import svd
from sklearn.cluster import AffinityPropagation
from collections import defaultdict
from sklearn.feature_selection import RFE
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectFpr, chi2
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score
from sklearn import metrics

from syntactic_unit import SentenceUnit, WordUnit
from Textrank import textrank

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# MODEL FEATURIZING AND TRAINING METHODS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

def featurize(documents, surfaceFeatures):
    print "STAGE [3] -- FEATURIZING -- (TextRank, LexRank, LDA) ..."
    t0 = time.clock()

    features = []
    for docIndex, doc in enumerate(documents):
        documentFeatures = extract_document_wide_features(doc)
        documentFeatures.append(surfaceFeatures[docIndex])
        features += [ counter_sum(fl) for fl in izip(*documentFeatures) ]

    print "  -- Done. Took {0} seconds process time to featurize {1} vector(s)".format(time.clock() - t0, len(features))
    return features

def extract_document_wide_features(document):
    documentFeatures = []

    documentFeatures.append(textrank.textrank_keyphrase(document))
    documentFeatures.append(textrank.lexrank_keyphrase(document))
    documentFeatures.append(textrank.textrank_keyword(document))

    return documentFeatures

def counter_sum(counterTuple):
    counterSum = Counter()
    for ele in counterTuple:
        counterSum += ele
    return counterSum

# def lexrank_keyphrase(text):
#     results = []
#     for i in range(len(text)):
#         results.append(Counter({ 'LEXRANK_SCORE': 0.0 }))
#     return results

def train_and_print_results(features, labels, modelFunction):
    model, featMatrix, vectorizer = modelFunction(features, labels)
    scores = cross_val_score(model, featMatrix, labels, scoring="f1_macro") # accuracy, f1, log_loss
    #print model.coef_
    predictions = model.predict(featMatrix)
    print ""
    print metrics.classification_report(labels, predictions)
    return model, vectorizer

def train_classifier_log_reg(features, labels):
    print "STAGE [4] -- TRAINING MODEL -- Logistic Regression ..."
    print ""
    #print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    t0 = time.clock()

    vectorizer = DictVectorizer(sparse=False)
    feature_matrix = vectorizer.fit_transform(features) # Features = List of counters

    mod = LogisticRegression(fit_intercept=True, intercept_scaling=1, class_weight='auto')

    mod.fit_transform(feature_matrix, labels)

    print "  -- Done. Took {0} seconds process time to train {1} data points".format(time.clock() - t0, len(features))
    return mod, feature_matrix, vectorizer

def train_classifier_gaussian_NB(features, labels):
    print "STAGE [4] -- TRAINING MODEL -- Gaussian Naive Bayes ..."
    print " "
    #print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    t0 = time.clock()

    vectorizer = DictVectorizer(sparse=False)
    feature_matrix = vectorizer.fit_transform(features) # Features = List of counters

    mod = GaussianNB()

    mod.fit(feature_matrix, labels)

    print "  -- Done. Took {0} seconds process time to train {1} data points".format(time.clock() - t0, len(features))
    return mod, feature_matrix, vectorizer

def train_classifier_SVM(features, labels):
    print "STAGE [4] -- TRAINING MODEL -- Support Vector Machine (SVM) ..."
    print " "
    #print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    t0 = time.clock()

    vectorizer = DictVectorizer(sparse=False)
    feature_matrix = vectorizer.fit_transform(features) # Features = List of counters

    mod = svm.SVC()
    mod.fit(feature_matrix, labels)

    print "  -- Done. Took {0} seconds process time to train {1} data points".format(time.clock() - t0, len(features))
    return mod, feature_matrix, vectorizer

def evaluate_trained_classifier(model, feature_matrix, labels):
    """Evaluate model, the output of train_classifier, on the test data."""
    print "STAGE [5] -- TESTING -- Logistic Regression ..."
    #print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    t0 = time.clock()
    predictions = model.predict(feature_matrix)
    print "  -- Done. Took {0} seconds process time to test {1} data points".format(time.clock() - t0, len(labels))
    print cross_val_score(model, feature_matrix, labels, scoring="f1_macro")
    return metrics.classification_report(labels, predictions)

# ---------------------------------------------------------------
# RANDOM NOTES:
# ---------------------------------------------------------------

# SET FEATURES AND LABELS:
# def featurize(summaries, bodies, summarySF, bodySF):
#     LABELS = ['SUMMARY', 'BODY']
#     features = []
#     labels = []
#     for docIndex in range(len(summaries)):
#         allSummFeatures = [ summarySF[docIndex][i] + extract_features(s) for i, s in enumerate(summaries[docIndex]) ]
#         allBodyFeatures = [ bodySF[docIndex][i] + extract_features(s) for i, s in enumerate(bodies[docIndex]) ]
#         labels += [LABELS[0]] * len(allSummFeatures) + [LABELS[1]] * len(allBodyFeatures)
#         features += allSummFeatures + allBodyFeatures
#     vectorizer = DictVectorizer(sparse=False)
#     feature_matrix = vectorizer.fit_transform(features) # Features = List of training counters
#     return feature_matrix, labels

# INTERMIX FEATURES:
# ---------------------------------------------------------------
# ['1', '2', '3'] and ['a', 'b', 'c', 'd'] => ['1', 'a', '2', 'b', '3', 'c', 'd']
# features = [x for x in itertools.chain.from_iterable(itertools.izip_longest(summaryFeatures, bodyFeatures)) if x]
# labels = [x for x in itertools.chain.from_iterable(itertools.izip_longest(summLabels, bodyLabels)) if x]

# def evaluate_trained_classifier(model=None, reader=sick_dev_reader):
#     """Evaluate model, the output of train_classifier, on the data in reader."""
#     mod, vectorizer, feature_selector, feature_function = model
#     feats, labels = featurizer(reader=reader, feature_function=feature_function)
#     feat_matrix = vectorizer.transform(feats)
#     if feature_selector:
#         feat_matrix = feature_selector.transform(feat_matrix)
#     predictions = mod.predict(feat_matrix)
#     return metrics.classification_report(labels, predictions)