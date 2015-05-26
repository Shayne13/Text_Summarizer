#!/usr/bin/env python

import sys, os, nltk, codecs
from pyquery import PyQuery as pq
from nltk import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# XML PARSER FUNCTIONS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

sentenceDetector = nltk.data.load('tokenizers/punkt/english.pickle')
stopwords = stopwords.words('english')

# ------------------------------------
# Args:
#   [1] (string) source folder of xml files.
#   [2] (string) destination folder for parsed output.
#   [3] (int) parsing flag:
#     0: Extract gold summaries and write to [2].
#     1: Extract surface features for body and write to [2].
# EG: python parser.py sample_rawdata sample_gold 0
# ------------------------------------
# Contains all parsing functions and surface feature extractors.
# ------------------------------------
def parse_folder(folder, output, flag):

  allSentences = []
  allSurfaceFeatures = []
  # print "Parsing files in: {0} ...".format(folder)
  
  for i, f in enumerate(os.listdir(folder)):
    # codecs.open('C:\Python26\text.txt', 'r', 'utf-8-sig')
    key = f.split('.')[0]
    d = pq(filename = "./{0}/{1}".format(folder, f))

    if flag == 0: # Extract and write gold summaries to output folder:

      title, goldSummarySentences, processedSummary, summaryFeatures = parse_summary(d)
      goldFilename = '{0}/gold_{1}.txt'.format(output, key)
      with codecs.open(goldFilename, 'w', 'utf-8-sig') as gf: gf.write(u'\n'.join(goldSummarySentences))
      allSentences.append(processedSummary)
      allSurfaceFeatures.append(summaryFeatures)
      # print "[{0}] Summary for {1} ({2})  --->  {3}".format(i, f, title, goldFilename)

    elif flag == 1: # Extract surface features from body and write to output folder:

      sentences, processedSentences, fileSurfaceFeatures = parse_body(d)
      trainExFilename = '{0}/train_{1}.txt'.format(output, key)
      with codecs.open(trainExFilename, 'w', 'utf-8-sig') as ff: ff.write(u'\n'.join(sentences))
      allSentences.append(processedSentences)
      allSurfaceFeatures.append(fileSurfaceFeatures)
      # print "[{0}] Parsing: {1}".format(i, f)

    else:

      print 'Invalid flag argument.'

  return allSentences, allSurfaceFeatures


# Fn: parse_summary( <pyquery xml document> )
# ----------------------------------------------------------------
# Returns title and summary as text, and summary features as a list.
# ----------------------------------------------------------------
def parse_summary(d):
  title = d('title').text()
  summary = []
  taggedSummary = []
  summaryFeatures = []
  summaryElem = d('summary')
  fullSummary = u' '.join([ c.text for c in summaryElem.children() ])
  summaryAsListOfSentences = sentenceDetector.tokenize(fullSummary)
  for s in summaryAsListOfSentences:
    processedSentence, surfaceFeatures = process_sentence(s)
    summaryFeatures.append(surfaceFeatures)
    taggedSummary.append(processedSentence)
    summary.append(s)
  return title, summary, taggedSummary, summaryFeatures


# Fn: parse_body( <pyquery xml document>, <nltk sentence detector> )
# ----------------------------------------------------------------
# Returns list of sentences and features for those sentences.
# ----------------------------------------------------------------
def parse_body(document):
  articleFeatureSet = []
  cleanedArticleSentences = []
  articleSentences = []
  bodyElem = document('body')

  for sect in bodyElem('section').items():
    for paragraphElem in sect('p').items():
      sentences = sentenceDetector.tokenize(paragraphElem.text().strip())
      l = len(sentences)
      for i, sentence in enumerate(sentences):
        processedSentence, surfaceFeatures = process_sentence(sentence)  
        articleFeatureSet.append(surfaceFeatures)
        cleanedArticleSentences.append(processedSentence)
        articleSentences.append(sentence)

  return articleSentences, cleanedArticleSentences, articleFeatureSet




# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SUFRACE FEATURE EXTRACTORS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

def process_sentence(sentence):
    surfaceFeatures = Counter()
    
    sentence_length(surfaceFeatures, sentence)
    # paragraph_position(surfaceFeatures, i, l)
    
    words = word_tokenize(sentence)
    taggedSentence = nltk.pos_tag(words)
    cleanedSentence = [ w for w in taggedSentence if w[0] not in stopwords ]
    
    return cleanedSentence, surfaceFeatures


def sentence_length(c, s):
  l = len(s.split(' ')) # TODO: Alternative to this with nltk?
  if l <= 10:
    c.update({ "SF_LENGTH_1" : 1.0 })
  elif l <= 20:
    c.update({ "SF_LENGTH_2" : 1.0 })
  elif l <= 30:
    c.update({ "SF_LENGTH_3" : 1.0 })
  else:
    c.update({ "SF_LENGTH_4" : 1.0 })

def paragraph_position(c, i, l):
  if i == 0: # First sentence in it's paragraph:
    c.update({ "PARAGRAPH_START_POS" : 1.0 })
  elif i == l - 1: # Middle sentence in it's paragraph:
    c.update({ "PARAGRAPH_END_POS" : 1.0 })
  else: # Last sentence in it's paragraph:
    c.update({ "PARAGRAPH_MID_POS" : 1.0 })

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SCRIPT EXECUTION:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# if __name__ == '__main__':
#   parse_folder(folder, output, flag)













