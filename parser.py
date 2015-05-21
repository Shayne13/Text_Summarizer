#!/usr/bin/env python

import sys, os, nltk, codecs
from pyquery import PyQuery as pq
from nltk import word_tokenize
from collections import Counter

# ------------------------------------
# Args:
#   [1] folder of xml files.
# EG: python parser.py small_data_sample
# ------------------------------------
# Parses all xml files, extracting the title, summary and body text.
# ------------------------------------

# Arg Check:
# ------------------------------------
if len(sys.argv) != 4:
  sys.exit('''Please pass in the following arguments:
1. The folder of xml files to be parsed.
2. The output folder for parsed files.
3. The flag indicating what to extract.''')

folder = sys.argv[1]
output = sys.argv[2]
flag = int(sys.argv[3])

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# XML PARSER FUNCTIONS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# Fn: parse_folder( <folder of xml documents (string)> , <flag> )
# ----------------------------------------------------------------
# Args:
#   [1] string: folder of xml documents
#   [2] string: output folder for parsed files
#   [3] int:
#       0 - BODY
#       1 - Writes gold summaries to output folder
# Parses all files in the folder, writing txt files to output folder ...
# ----------------------------------------------------------------
def parse_folder(folder, output, flag):
  print "Parsing files in: {0} ...".format(folder)
  sentenceDetector = nltk.data.load('tokenizers/punkt/english.pickle')
  for i, f in enumerate(os.listdir(folder)):
    d = pq(filename = "./{0}/{1}".format(folder, f))
    key = f.split('.')[0]
    if flag == 0: # Extract surface features from body and write to output folder:
      print "[{0}] Parsing: {1}".format(i, f)
      fileSurfaceFeatures = parse_body(d, sentenceDetector)
      contents = [ "{0}: {1}".format(k, v) for k, v in fileSurfaceFeatures.items() ]
      featureFilename = '{0}/features_{1}.txt'.format(output, key)
      with open(featureFilename, 'w') as ff: ff.write (str(contents))
    elif flag == 1: # Extract and write gold summaries to output folder:
      title, goldSummary = parse_summary(d)
      goldFilename = '{0}/gold_{1}.txt'.format(output, key)
      with open(goldFilename, 'w') as gf: gf.write (goldSummary)
      print "[{0}] Summary for {1} ({2})  --->  {3}".format(i, f, title, goldFilename)
    else:
      print 'Invalid flag argument.'


# Fn: parse_summary( <string path to xml file> )
# ----------------------------------------------------------------
# Returns title and summary as text, and body as map fromin contiguous
# text form, and body as a <pyquery>.
# ----------------------------------------------------------------
def parse_summary(d):
  title = d('title').text()
  summaryElem = d('summary')
  summary = ' '.join([ c.text.encode('utf-8') for c in summaryElem.children() ])
  return title, summary

def parse_body(d, sentenceDetector):
  articleFeatureSet = {}
  sentenceIndex = 0
  bodyElem = d('body')
  for sect in bodyElem('section').items():
    for paragraphElem in sect('p').items():
      sentences = sentenceDetector.tokenize(paragraphElem.text().strip())
      for s in sentences:
        surfaceFeatures = Counter({sentence_length_feature(s) : 1})
        articleFeatureSet[sentenceIndex] = surfaceFeatures
        sentenceIndex += 1
  return articleFeatureSet


  # position in paragraph
  # position in section
  # sentence length classes:
    # 1 - 6 words
    # 7 - 12 words
    # 13 - 24 words
    # 25 - 25+

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SUFRACE FEATURE EXTRACTORS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

def sentence_length_feature(s):
  l = len(s.split(' ')) # TODO: Alternative to this with nltk?
  if l <= 10:
    return "SF_LENGTH_1"
  elif l <= 20:
    return "SF_LENGTH_2"
  elif l <= 30:
    return "SF_LENGTH_3"
  else:
    return "SF_LENGTH_4"

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SCRIPT EXECUTION:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

if __name__ == '__main__':
  parse_folder(folder, output, flag)


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# RANDOM NOTES:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# import script as though it is a module to run functions from it.
# s = f('summary')
# s.text()
# len(s)
# dir(s)
# type(s)










