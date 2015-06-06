
# coding: utf-8

# In[26]:

from parser import *

import itertools
import random
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
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score
from sklearn import metrics


# In[27]:

from summanlp_textrank import commons, graph, keywords, pagerank_weighted,                   summarizer, textrank, textcleaner, textrank_runtime_error


# In[28]:

#get_ipython().magic(u'load_ext autoreload')


# In[29]:

# To reload: 
#get_ipython().magic(u'autoreload')


# In[30]:

inputXML = "sample_1"
# inputXML = "sample_rawXML"
summaryFolder = "sample_summary"
bodyFolder = "sample_body"


# In[31]:

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# PARSE:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
documents, labels = parse_xml_folder(inputXML, summaryFolder, bodyFolder, writeOption='none')
surfaceFeatures = process_data(documents)


# In[32]:

def featurize(documents, surfaceFeatures):
    print "STAGE [3] -- FEATURIZING -- (TextRank, LexRank, LDA) ..."
    features = []
    for docIndex, doc in enumerate(documents):
        documentFeatures = extract_document_wide_features(doc)
        documentFeatures.append(surfaceFeatures[docIndex])
        features += [ counter_sum(fl) for fl in izip(*documentFeatures) ]
    return features


# In[33]:

def extract_document_wide_features(document):
    documentFeatures = []

    documentFeatures.append(textrank_keyphrase(document))
    documentFeatures.append(lexrank_keyphrase(document))
    documentFeatures.append(textrank_keyword(document))

    return documentFeatures


# In[34]:

def counter_sum(counterTuple):
    counterSum = Counter()
    for ele in counterTuple:
        counterSum += ele
    return counterSum


# In[35]:

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


# In[36]:

def textrank_keyword(text):
    txt = u' '.join([ su.text for su in text ])
    # Gets a dict of word -> lemma
    tokens = textcleaner.clean_text_by_word(text, 'english')
    split_text = list(textcleaner.tokenize_by_word(txt))

    # Creates the graph and adds the edges
    graph = commons.build_graph(keywords._get_words_for_graph(tokens))
    keywords._set_graph_edges(graph, tokens, split_text)
    del split_text # It's no longer used
    commons.remove_unreachable_nodes(graph)

    # # Ranks the tokens using the PageRank algorithm. Returns dict of lemma -> score
    pagerank_scores = keywords._pagerank_word(graph)
    extracted_lemmas = keywords._extract_tokens(graph.nodes(), pagerank_scores, 0.2, None)
    lemmas_to_word = keywords._lemmas_to_words(tokens)
    keyWords = keywords._get_keywords_with_score(extracted_lemmas, lemmas_to_word)
    # # text.split() to keep numbers and punctuation marks, so separeted concepts are not combined
    combined_keywords = keywords._get_combined_keywords(keyWords, txt.split())
    kw_scores = keywords._format_results(keyWords, combined_keywords, False, True)

    results = [ Counter({ 'TEXTRANK_KEYWORD_SCORE': keyword_mean_score(su.basic, kw_scores) }) for su in text ]
    return results


# In[37]:

def keyword_mean_score(sentence, wordScores):
    totalScore = sum([ s for w, s in wordScores if w in sentence ])
#     print sentence.split()
    if not sentence.split(): return 0.0
    return totalScore / len(sentence.split())


# In[38]:

def lexrank_keyphrase(text):
    results = []
    for i in range(len(text)):
        results.append(Counter({ 'LEXRANK_SCORE': 0.0 }))
    return results


# In[ ]:

def train_classifier(features, labels):
    print "STAGE [4] -- TRAINING MODEL -- Logistic Regression ..."
    print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    vectorizer = DictVectorizer(sparse=False)
    feature_matrix = vectorizer.fit_transform(features) # Features = List of counters
    mod = LogisticRegression(fit_intercept=True, intercept_scaling=1, class_weight='auto')
    mod.fit_transform(feature_matrix, labels)
    return mod, feature_matrix, vectorizer


# In[40]:

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# TRAIN:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
features = featurize(documents, surfaceFeatures)
# del surfaceFeatures
model, featMatrix, vectorizer = train_classifier(features, labels)

scores = cross_val_score(model, featMatrix, labels, scoring="f1_macro") # accuracy, f1, log_loss
print model.coef_
predictions = model.predict(featMatrix)
print metrics.classification_report(labels, predictions)


# In[41]:

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# TEST:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
testXMLFolder = "sample_test"
testDocuments, testLabels = parse_xml_folder(testXMLFolder, summaryFolder, bodyFolder, writeOption='none')
testSurfaceFeatures = process_data(testDocuments)


# In[42]:

testFeatures = featurize(testDocuments, testSurfaceFeatures)
testFeatureMatrix = vectorizer.transform(testFeatures) # Features = List of counters
# del testSurfaceFeatures


# In[43]:

def evaluate_trained_classifier(model, feature_matrix, labels):
    """Evaluate model, the output of train_classifier, on the test data."""
    print "STAGE [5] -- TESTING -- Logistic Regression ..."
    print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    predictions = model.predict(feature_matrix)
    print cross_val_score(model, feature_matrix, labels, scoring="f1_macro")
    return metrics.classification_report(labels, predictions)


# In[44]:

print evaluate_trained_classifier(model, testFeatureMatrix, testLabels)


# In[45]:

def extract_summary(document):
    summary = []
    for su in document:
        if su.label == 'summary':
            summary.append(su.text)
        else:
            break
    return summary


# In[46]:

from heapq import nlargest

def extract_top_ranked(document, featureMatrix, num):
    predictions = model.predict_proba(featureMatrix)
    itr = range(len(document))
    topIndexes = nlargest(num, itr, key=lambda i: predictions[i][1])
    topSentences = [ document[index].text for index in topIndexes]
    return topSentences


# In[47]:

featIndex = 0
rouge_gold_summaries = []
rouge_generated_summaries = []
for i, tdoc in enumerate(testDocuments):
    numSentences = len(tdoc)
    rouge_gold_summaries.append(extract_summary(tdoc))
    rouge_generated_summaries.append(extract_top_ranked(tdoc, testFeatureMatrix[featIndex:featIndex+numSentences], 10))
    featIndex += numSentences

#print rouge_gold_summaries
#print rouge_generated_summaries


# In[48]:

import pickle


# In[69]:

pickle_gold_summaries = {}
pickle_generated_summaries = {}
for i in range(len(rouge_gold_summaries)):
    pickle_gold_summaries[i] = rouge_gold_summaries[i]
    pickle_generated_summaries[i] = rouge_generated_summaries[i]


# In[79]:

pickle.dump( pickle_gold_summaries, open( "pickle_gold_summaries.p", "wb" ) )
pickle.dump( pickle_generated_summaries, open( "pickle_generated_summaries.p", "wb" ) )


# In[80]:

# get_ipython().magic(u'autoreload')
#from RougeRunner import *

#rougeResults = []

#loaded_gold_summaries = pickle.load(open( "pickle_gold_summaries.p", "rb" ) )
#loaded_generated_summaries = pickle.load( open( "pickle_generated_summaries.p", "rb" ) )

#for summaryIndex in range(len(loaded_gold_summaries)):
#    gold = loaded_gold_summaries[summaryIndex]
##    genSum = loaded_generated_summaries[summaryIndex]
#    rougeResults.append(compareUsingRouge(gold, genSum))
    
#print rougeResults


# In[ ]:



