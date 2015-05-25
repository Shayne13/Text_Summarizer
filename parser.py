#!/usr/bin/env python

import sys, os, nltk, codecs
from pyquery import PyQuery as pq
from nltk import word_tokenize
from collections import Counter

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# XML PARSER FUNCTIONS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

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
  sentenceDetector = nltk.data.load('tokenizers/punkt/english.pickle')
  for i, f in enumerate(os.listdir(folder)):
    # codecs.open('C:\Python26\text.txt', 'r', 'utf-8-sig')
    key = f.split('.')[0]
    d = pq(filename = "./{0}/{1}".format(folder, f))

    if flag == 0: # Extract and write gold summaries to output folder:

      title, goldSummarySentences, summaryFeatures = parse_summary(d, sentenceDetector)
      goldFilename = '{0}/gold_{1}.txt'.format(output, key)
      with codecs.open(goldFilename, 'w', 'utf-8-sig') as gf: gf.write(u'\n'.join(goldSummarySentences))

      # with open(goldFilename, 'w') as gf: gf.write ('\n'.join(goldSummarySentences))
      # print "[{0}] Summary for {1} ({2})  --->  {3}".format(i, f, title, goldFilename)
      allSentences.append(goldSummarySentences)
      allSurfaceFeatures.append(summaryFeatures)

    elif flag == 1: # Extract surface features from body and write to output folder:

      # print "[{0}] Parsing: {1}".format(i, f)
      sentences, fileSurfaceFeatures = parse_body(d, sentenceDetector)
      trainExFilename = '{0}/train_{1}.txt'.format(output, key)
      with codecs.open(trainExFilename, 'w', 'utf-8-sig') as ff: ff.write(u'\n'.join(sentences))

      # with open(trainExFilename, 'w') as ff: ff.write ('\n'.join(sentences))
      allSentences.append(sentences)
      allSurfaceFeatures.append(fileSurfaceFeatures)

    else:

      print 'Invalid flag argument.'

  return allSentences, allSurfaceFeatures


# Fn: parse_summary( <pyquery xml document> )
# ----------------------------------------------------------------
# Returns title and summary as text, and summary features as a list.
# ----------------------------------------------------------------
def parse_summary(d, sentenceDetector):
  title = d('title').text()
  summaryElem = d('summary')
  fullSummary = u' '.join([ c.text for c in summaryElem.children() ])
  summary = sentenceDetector.tokenize(fullSummary)
  summaryFeatures = [ get_surface_features(s) for s in summary ]
  return title, summary, summaryFeatures


# Fn: parse_body( <pyquery xml document>, <nltk sentence detector> )
# ----------------------------------------------------------------
# Returns list of sentences and features for those sentences.
# ----------------------------------------------------------------
def parse_body(document, sentenceDetector):
  articleFeatureSet = []
  articleSentences = []
  bodyElem = document('body')
  for sect in bodyElem('section').items():
    for paragraphElem in sect('p').items():
      sentences = sentenceDetector.tokenize(paragraphElem.text().strip())
      l = len(sentences)
      for i, sentence in enumerate(sentences):
        articleFeatureSet.append(get_surface_features(sentence))
        articleSentences.append(sentence)
  return articleSentences, articleFeatureSet


def get_surface_features(sentence):
    surfaceFeatures = Counter()

    sentence_length(surfaceFeatures, sentence)
    # paragraph_position(surfaceFeatures, i, l)

    return surfaceFeatures


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SUFRACE FEATURE EXTRACTORS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

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













