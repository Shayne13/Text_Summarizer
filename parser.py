#!/usr/bin/env python

import sys, os, nltk, codecs, itertools
from pyquery import PyQuery as pq
from nltk import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from syntactic_units import SentenceUnit, WordUnit

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# XML PARSER FUNCTIONS:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# Loading Sentence Detector and Stop Words List
sentenceDetector = nltk.data.load('tokenizers/punkt/english.pickle')
stopwords = stopwords.words('english')

# parse_and_process_xml(string, string, string, string)
# ------------------------------------------------------------------------------
# [1] Source folder of xml files.
# [2] Destination folder for summaries.
# [3] Destination folder for bodies.
# [4] Writing flag:
#     'summary': Extract gold summary sentences and write to [2].
#     'body': Extract body sentences and write to [3].
#     'both': Extract gold summary and body sentences  and write to [2] and [3].
#     'none': Do not write to any files.
# ------------------------------------------------------------------------------
# Parses then processes a folder of xml files, returning the processed summaries
# and bodies and their respective surface features in the form of:
# [ [ps_1, ps_1, ps_1], [ps_2, ps_2, ps_2, ps_2], [ps_3, ps_3], ... ]
# where ps_1 = processed_sentence for document 1. Surface features are represented
# as lists of lists of counter collections, also partitioned by document.
# ------------------------------------------------------------------------------
def parse_and_process_xml(inputFolder, summaryFolder, bodyFolder, writeOption=None):
    summaries, bodies = parse_xml_folder(inputFolder, summaryFolder, bodyFolder, writeOption)
    summarySF = process_data(summaries)
    bodySF = process_data(bodies)
    return summaries, bodies, summarySF, bodySF

# parse_xml_folder(string, string, string, string)
# ------------------------------------------------------------------------------
# [1] Source folder of xml files.
# [2] Destination folder for summaries.
# [3] Destination folder for bodies.
# [4] Writing flag:
#     'summary': Extract gold summary sentences and write to [2].
#     'body': Extract body sentences and write to [3].
#     'both': Extract gold summary and body sentences  and write to [2] and [3].
#     'none': Do not write to any files.
# ------------------------------------------------------------------------------
# Parses a folder of xml files, returning the parsed summaries and bodies in
# the form of: [ [s_1, s_1, s_1], [s_2, s_2, s_2, s_2], [s_3, s_3], ... ]
# where s_1 = sentence for document 1 (either body or summary).
# ------------------------------------------------------------------------------
def parse_xml_folder(inputFolder, summaryFolder, bodyFolder, writeOption=None):
    print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    print 'STAGE [1] -- PARSING XML -- from {0} ...'.format(inputFolder)
    XMLFiles = os.listdir(inputFolder)
    articles = [ pq(filename = "./{0}/{1}".format(inputFolder, f)) for i, f in enumerate(XMLFiles) ]
    summaries = [ parse_xml_document(d, 'summary') for d in articles ]
    bodies = [ parse_xml_document(d, 'body') for d in articles ]

    if writeOption:
        if writeOption == 'summary':
            print 'STAGE [1.1] -- WRITING TXT -- summaries to {0}/ ...'.format(summaryFolder)
            write_folder(XMLFiles, summaryFolder + '/summary_', summaries)
        elif writeOption == 'body':
            print 'STAGE [1.1] -- WRITING TXT -- bodies to {0}/ ...'.format(bodyFolder)
            write_folder(XMLFiles, bodyFolder + '/body_', bodies)
        elif writeOption == 'both':
            print 'STAGE [1.1] -- WRITING TXT -- summaries --> {0}/,  bodies --> {1}/ ...'.format(summaryFolder, bodyFolder)
            write_folder(XMLFiles, summaryFolder + '/summary_', summaries)
            write_folder(XMLFiles, bodyFolder + '/body_', bodies)

    LABELS = ['SUMMARY', 'BODY']
    documents = [ summaries[i] + bodies[i] for i in range(len(articles)) ]
    labels = list(itertools.chain(*[([LABELS[0]]*len(summaries[i])) + ([LABELS[1]]*len(bodies[i])) for i in range(len(articles))]))

    return documents, labels

# parse_xml_document( <pyquery document>, string)
# ------------------------------------------------------------------------------
# [1] PyQuery document entity.
# [2] PyQuery document entity name to extract: 'summary' or 'body'.
# ------------------------------------------------------------------------------
# Returns a list of sentences from either the summary or body for
# that document.
# ------------------------------------------------------------------------------
def parse_xml_document(d, entity):
    elem = d(entity)
    if elem:
        text = u' '.join([ p.text().strip() for p in elem('p').items() ])
        sentences = sentenceDetector.tokenize(text)
        return [ SentenceUnit(sentence, entity.encode('utf-8'), i) for i, sentence in enumerate(sentences) ]
    else:
        print 'Error: Invalid arguments to parse_xml_document.'
        return

# write_folder( [string], string, [[string]] )
# ------------------------------------------------------------------------------
# [1] List of xml file names for their keys.
# [2] Name of output file: 'sample_gold/<key>'.
# [3] List of lists of sentences to be written to output txt file.
# ------------------------------------------------------------------------------
# Writes '\n' separated sentences to txt files in the specified folder.
# ------------------------------------------------------------------------------
def write_folder(XMLFileNames, outputName, text):
    fileNames = [ '{0}.txt'.format(outputName + xfn.split('.')[0]) for xfn in XMLFileNames ]
    for docIndex, fn in enumerate(fileNames):
        with codecs.open(fn, 'w', 'utf-8-sig') as f: f.write(u'\n'.join( [ su.text for su in text[docIndex] ]))


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# PROCESS DATA:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>


# process_data( [[string]], string )
# ------------------------------------------------------------------------------
# [1] List of lists of sentences to be processed.
# [2] Name of folder of txt files: '\n' separated, parsed sentences.
# [3] List of sentences to be written to output txt file.
# ------------------------------------------------------------------------------
# Returns processed sentences with their surface features in the form of:
# [ [ps_1, ps_1, ps_1], [ps_2, ps_2, ps_2, ps_2], [ps_3, ps_3], ... ]
# where ps_1 = processed_sentence for document 1. Surface features are represented
# as lists of lists of counter collections, also partitioned by document..
# ------------------------------------------------------------------------------
def process_data(data):
    print 'STAGE [2] -- PROCESSING DATA -- (tokenizing/tagging/stopwords/extracting) ...'
    surfaceFeatures = []
    for document in data:
        surfaceFeatures.append([ process_sentence(su) for su in document ])
    return surfaceFeatures


# process_sentence( string )
# ------------------------------------------------------------------------------
# [1] A sentence.
# ------------------------------------------------------------------------------
# Returns the processed sentence (POS tagged/stopwords) and it's surface features.
# ------------------------------------------------------------------------------
def process_sentence(sentenceUnit):

    sentence = sentenceUnit.text
    words = word_tokenize(sentence)
    tagged = nltk.pos_tag(words) # Add POS tags
    cleaned = [ w for w in tagged if w[0] not in stopwords ] # Remove stopwords
    processed = [ w for w in cleaned if w[1] in ['NN', 'NNS','NNP', 'NNPS', 'JJ', 'JJR', 'JJS'] ] # Removes non-adj, non-noun
    sentenceUnit.processed = processed
    # sentenceUnit.token = u' '.join([ w[0] for w in processed ]) if processed else u''

    surfaceFeatures = extract_surface_features(sentence, cleaned)

    return surfaceFeatures

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# EXTRACT SURFACE FEATURES:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

def extract_surface_features(sentence, tagged):
    surfaceFeatures = Counter()

    sentence_length(surfaceFeatures, sentence)
    contains_punctuation(surfaceFeatures, sentence, '!') # TODO: Check this is finding appropriately.
    contains_punctuation(surfaceFeatures, sentence, '?')
    contains_punctuation(surfaceFeatures, sentence, "\'")
    contains_punctuation(surfaceFeatures, sentence, "(")
    contains_punctuation(surfaceFeatures, sentence, "-")
    contains_punctuation(surfaceFeatures, sentence, ".")

    contains_word_type(surfaceFeatures, tagged, ['NN', 'NNS'])
    contains_word_type(surfaceFeatures, tagged, ['JJ', 'JJR', 'JJS'])
    contains_word_type(surfaceFeatures, tagged, ['NNP', 'NNPS'])
    contains_word_type(surfaceFeatures, tagged, ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'])
    contains_word_type(surfaceFeatures, tagged, ['RB', 'RBR', 'RBS'])
    contains_word_type(surfaceFeatures, tagged, ['CD'])

    word_type_ratio(surfaceFeatures, tagged, ['NN', 'NNS', 'NNP', 'NNPS'])
    word_type_ratio(surfaceFeatures, tagged, ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'])
    word_type_ratio(surfaceFeatures, tagged, ['JJ', 'JJR', 'JJS'])
    word_type_ratio(surfaceFeatures, tagged, ['RB', 'RBR', 'RBS'])

    ratio_important_words(surfaceFeatures, sentence, tagged)

    return surfaceFeatures

# sentence_length( counter, string )
# ------------------------------------------------------------------------------
# [1] A counter for surface features.
# [2] A sentence (to measure it's length).
# ------------------------------------------------------------------------------
# Updates the counter to add this feature.
# ------------------------------------------------------------------------------
def sentence_length(c, s):
    l = len(word_tokenize(s))
    # l = len(s.split(' '))
    if l <= 10:
        c.update({ "SENTENCE_LENGTH_1" : 1.0 })
    elif l <= 20:
        c.update({ "SENTENCE_LENGTH_2" : 1.0 })
    elif l <= 30:
        c.update({ "SENTENCE_LENGTH_3" : 1.0 })
    else:
        c.update({ "SENTENCE_LENGTH_4" : 1.0 })

def contains_punctuation(c, s, p):
    if p in s:
        c.update({ "CONTAINS_PUNCTUATION_{0}".format(p) : 1.0 })

def contains_word_type(c, t, tags):
    for w in t:
        if w[1] in tags:
            c.update({ "CONTAINS_WORD_TYPE_{0}".format(tags[0]) : 1.0 })
            break

def word_type_ratio(c, t, tags):
    ratio = sum(1.0 for w in t if w[1] in tags) / (len(t) * 1.0)
    c.update({ "WORD_RATIO_{0}".format(tags[0]) : ratio })

def ratio_important_words(c, s, t):
    ratio = len(t) / len(word_tokenize(s))
    c.update({ "IMPORTANT_WORD_RATIO" : ratio })

# paragraph_position( counter, int, int )
# ------------------------------------------------------------------------------
# [1] A counter for surface features.
# [2] Sentence's number in it's pargraph.
# [3] Size of sentence's paragraph.
# ------------------------------------------------------------------------------
# Updates the counter to add this feature.
# ------------------------------------------------------------------------------
def paragraph_position(c, i, l):
    if i == 0: # First sentence in it's paragraph:
        c.update({ "PARAGRAPH_START_POS" : 1.0 })
    elif i == l - 1: # Middle sentence in it's paragraph:
        c.update({ "PARAGRAPH_END_POS" : 1.0 })
    else: # Last sentence in it's paragraph:
        c.update({ "PARAGRAPH_MID_POS" : 1.0 })

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# SCRIPT EXECUTION:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

# if __name__ == '__main__':
#   parse_folder(folder, output, flag)


# def is_noun(tag):
#     return tag in ['NN', 'NNS', 'NNP', 'NNPS']

# def is_verb(tag):
#     return tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']

# def is_adverb(tag):
#     return tag in ['RB', 'RBR', 'RBS']

# def is_adjective(tag):
#     return tag in ['JJ', 'JJR', 'JJS']










