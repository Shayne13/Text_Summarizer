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

  print "Parsing files in: {0} ...".format(folder)
  sentenceDetector = nltk.data.load('tokenizers/punkt/english.pickle')
  for i, f in enumerate(os.listdir(folder)):
    key = f.split('.')[0]
    d = pq(filename = "./{0}/{1}".format(folder, f))

    if flag == 0: # Extract and write gold summaries to output folder:

      title, goldSummary = parse_summary(d)
      goldFilename = '{0}/gold_{1}.txt'.format(output, key)
      with open(goldFilename, 'w') as gf: gf.write (goldSummary)
      print "[{0}] Summary for {1} ({2})  --->  {3}".format(i, f, title, goldFilename)

    elif flag == 1: # Extract surface features from body and write to output folder:

      print "[{0}] Parsing: {1}".format(i, f)
      sentences, fileSurfaceFeatures = parse_body(d, sentenceDetector)
      contents = [ "{0}: {1}".format(k, v) for k, v in sentences.items() ]
      trainExFilename = '{0}/train_{1}.txt'.format(output, key)
      with open(trainExFilename, 'w') as ff: ff.write (str(contents))
      allSentences.append(sentences)
      allSurfaceFeatures.append(fileSurfaceFeatures)

    else:
      print 'Invalid flag argument.'

  return allSentences, allSurfaceFeatures


# Fn: parse_summary( <pyquery xml document> )
# ----------------------------------------------------------------
# Returns title and summary as text.
# ----------------------------------------------------------------
def parse_summary(d):
  title = d('title').text()
  summaryElem = d('summary')
  summary = ' '.join([ c.text.encode('utf-8') for c in summaryElem.children() ])
  return title, summary


# Fn: parse_body( <pyquery xml document>, <nltk sentence detector> )
# ----------------------------------------------------------------
# Returns title and summary as text.
# ----------------------------------------------------------------
def parse_body(d, sentenceDetector):
  articleFeatureSet = {}
  articleSentences = {}
  sentenceIndex = 0
  bodyElem = d('body')
  for sect in bodyElem('section').items():
    for paragraphElem in sect('p').items():
      sentences = sentenceDetector.tokenize(paragraphElem.text().strip())
      l = len(sentences)
      for i, s in enumerate(sentences):
        surfaceFeatures = Counter()

        sentence_length(surfaceFeatures, s)
        paragraph_position(surfaceFeatures, i, l)

        articleFeatureSet[sentenceIndex] = surfaceFeatures
        articleSentences[sentenceIndex] = s.encode("ascii","ignore")
        sentenceIndex += 1
  return articleSentences, articleFeatureSet


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SUFRACE FEATURE EXTRACTORS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

def sentence_length(c, s):
  l = len(s.split(' ')) # TODO: Alternative to this with nltk?
  if l <= 10:
    c.update({ "SF_LENGTH_1" : 1 })
  elif l <= 20:
    c.update({ "SF_LENGTH_2" : 1 })
  elif l <= 30:
    c.update({ "SF_LENGTH_3" : 1 })
  else:
    c.update({ "SF_LENGTH_4" : 1 })

def paragraph_position(c, i, l):
  if i == 0: # First sentence in it's paragraph:
    c.update({ "PARAGRAPH_START_POS" : 1 })
  elif i == l - 1: # Middle sentence in it's paragraph:
    c.update({ "PARAGRAPH_END_POS" : 1 })
  else: # Last sentence in it's paragraph:
    c.update({ "PARAGRAPH_MID_POS" : 1 })

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SCRIPT EXECUTION:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# if __name__ == '__main__':
#   parse_folder(folder, output, flag)













