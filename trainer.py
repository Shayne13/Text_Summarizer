import itertools
import random
import pickle
import numpy as np
from operator import itemgetter
from collections import Counter
from itertools import izip
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

from summanlp_textrank.syntactic_unit import SyntacticUnit
from summanlp_textrank import commons, graph, keywords, pagerank_weighted, \
                  summarizer, textrank, textcleaner, textrank_runtime_error

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# MODEL FEATURIZING AND TRAINING METHODS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# SET FEATURES AND LABELS:
def featurize(documents, surfaceFeatures):
    print "STAGE [3] -- FEATURIZING -- (TextRank, LexRank, LDA) ..."
    features = []
    for docIndex, doc in enumerate(documents):
        documentFeatures = extract_document_wide_features(doc)
        documentFeatures.append(surfaceFeatures[docIndex])
        features += [ counter_sum(fl) for fl in izip(*documentFeatures) ]
    return features

def extract_document_wide_features(document):
    documentFeatures = []

    documentFeatures.append(textrank_keyphrase(document))
    documentFeatures.append(lexrank_keyphrase(document))

    txt = ' '.join([ su.text for su in document ])
    keyWords = textrank_keyword(txt)
    print keyWords

    return documentFeatures

def counter_sum(counterTuple):
    counterSum = Counter()
    for ele in counterTuple:
        counterSum += ele
    return counterSum

def textrank_keyphrase(text):

    # Creates the graph and calculates the similarity coefficient for every pair of nodes.
    graph = commons.build_graph([ syntacticUnit for syntacticUnit in text])
    summarizer._set_graph_edge_weights(graph)
    # Remove all nodes with all edges weights equal to zero.
    commons.remove_unreachable_nodes(graph)

    # Ranks the tokens using the PageRank algorithm. Returns dict of sentence -> score
    pagerank_scores = summarizer._pagerank(graph)

    # Adds the summa scores to the sentence objects.
    # summarizer._add_scores_to_sentences(sentences, pagerank_scores)

    results = []
    for su in text:
        score = (1-pagerank_scores[su.label, su.index]) if (su.label, su.index) in pagerank_scores.keys() else 0.0
        results.append(Counter({ 'TEXTRANK_SCORE': score }))
    return results

def textrank_keyword(text):
    # Gets a dict of word -> lemma
    tokens = textcleaner.clean_text_by_word(text, 'english')
    print tokens
    print '******************'
    split_text = list(textcleaner.tokenize_by_word(text))
    print split_text[0:6]
    print '******************'
    # Creates the graph and adds the edges
    graph = commons.build_graph(keywords._get_words_for_graph(tokens))
    keywords._set_graph_edges(graph, tokens, split_text)
    del split_text # It's no longer used

    commons.remove_unreachable_nodes(graph)

    # Ranks the tokens using the PageRank algorithm. Returns dict of lemma -> score
    pagerank_scores = keywords._pagerank(graph)

    extracted_lemmas = keywords._extract_tokens(graph.nodes(), pagerank_scores, ratio, words)
    print extracted_lemmas
    print '******************'
    lemmas_to_word = keywords._lemmas_to_words(tokens)
    print lemmas_to_words
    print '******************'
    keyWords = keywords._get_keywords_with_score(extracted_lemmas, lemmas_to_word)

    # text.split() to keep numbers and punctuation marks, so separeted concepts are not combined
    combined_keywords = keywords._get_combined_keywords(keyWords, text.split())

    return keywords._format_results(keyWords, combined_keywords, split, scores)

def lexrank_keyphrase(text):
    results = []
    for i in range(len(text)):
        results.append(Counter({ 'LEXRANK_SCORE': 0.0 }))
    return results

# TRAIN CLASSIFIER:
def train_classifier(features, labels):
    print "STAGE [4] -- TRAINING MODEL -- Logistic Regression ..."
    print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    vectorizer = DictVectorizer(sparse=False)
    feature_matrix = vectorizer.fit_transform(features) # Features = List of counters
    mod = LogisticRegression(fit_intercept=True, intercept_scaling=1, class_weight='auto')
    mod.fit_transform(feature_matrix, labels)
    return mod, feature_matrix

    # Return the trained model along with the objects we need to
    # featurize test data in a way that aligns with our training
    # matrix:
#     return (mod, vectorizer, feature_selector, feature_function)


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