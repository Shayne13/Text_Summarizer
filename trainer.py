import itertools
import random
import pickle
import numpy as np
from operator import itemgetter
import scipy
import scipy.spatial.distance
from numpy.linalg import svd
# For visualization:
# from tsne import tsne # See http://lvdmaaten.github.io/tsne/#implementations
# import matplotlib.pyplot as plt
# For clustering in the 'Word-sense ambiguities' section:
from sklearn.cluster import AffinityPropagation
from collections import defaultdict
from sklearn.feature_selection import RFE
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectFpr, chi2
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score
from sklearn import metrics

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# MODEL FEATURIZING AND TRAINING METHODS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# SET FEATURES AND LABELS:
def featurize(summarySF, bodySF):
    LABELS = ['SUMMARY', 'BODY']
    features = []
    labels = []
    for docIndex in range(len(summarySF)):
        features += summarySF[docIndex] + bodySF[docIndex]
        labels += [LABELS[0]] * len(summarySF[docIndex]) + [LABELS[1]] * len(bodySF[docIndex])
    vectorizer = DictVectorizer(sparse=False)
    feature_matrix = vectorizer.fit_transform(features) # Features = List of training counters
    return feature_matrix, labels

# TRAIN CLASSIFIER:
def trainClassifier(features, labels):
    mod = LogisticRegression(fit_intercept=True, intercept_scaling=1, class_weight='auto')
    mod.fit_transform(features, labels)
    return mod

    # Return the trained model along with the objects we need to
    # featurize test data in a way that aligns with our training
    # matrix:
#     return (mod, vectorizer, feature_selector, feature_function)




# def evaluate_trained_classifier(model=None, reader=sick_dev_reader):
#     """Evaluate model, the output of train_classifier, on the data in reader."""
#     mod, vectorizer, feature_selector, feature_function = model
#     feats, labels = featurizer(reader=reader, feature_function=feature_function)
#     feat_matrix = vectorizer.transform(feats)
#     if feature_selector:
#         feat_matrix = feature_selector.transform(feat_matrix)
#     predictions = mod.predict(feat_matrix)
#     return metrics.classification_report(labels, predictions)