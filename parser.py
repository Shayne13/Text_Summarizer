#!/usr/bin/env python

import sys, os, nltk, codecs
from pyquery import PyQuery as pq
from nltk import word_tokenize
from nltk.corpus import stopwords
from collections import Counter

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
    print '<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>'
    print 'STAGE [1] -- PARSING XML -- from {0} ...'.format(inputFolder)
    summaries, bodies = parse_xml_folder(inputFolder, summaryFolder, bodyFolder, writeOption)
    print 'STAGE [2] -- PROCESSING DATA -- (tokenizing/stopwords/stemming/translating) ...'
    p_summaries, summarySF = process_data(data=summaries)
    p_bodies, bodySF = process_data(data=bodies)
    return p_summaries, p_bodies, summarySF, bodySF

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
    XMLFiles = os.listdir(inputFolder)
    documents = [ pq(filename = "./{0}/{1}".format(inputFolder, f)) for i, f in enumerate(XMLFiles) ]
    summaries = [ parse_xml_document(d, 'summary') for d in documents ]
    bodies = [ parse_xml_document(d, 'body') for d in documents ]
    
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
            
    return summaries, bodies

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
        return sentenceDetector.tokenize(text)
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
        with codecs.open(fn, 'w', 'utf-8-sig') as f: f.write(u'\n'.join(text[docIndex]))
           
        
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
def process_data(data=None, inputFolder=None):
    processedData = []
    surfaceFeatures = []
    if data:
        for document in data:
            processedDoc = []
            documentSurfaceFeatures = []
            for s in document:
                processedSentence, sentenceSurfaceFeatures = process_sentence(s)
                processedDoc.append(processedSentence)
                documentSurfaceFeatures.append(sentenceSurfaceFeatures)
            processedData.append(processedDoc)
            surfaceFeatures.append(documentSurfaceFeatures)
        return processedData, surfaceFeatures
    elif inputFolder:
        return [], [] # TODO!
    else:
        print 'Error: Invalid arguments to clean_to_processed.'
        
# process_sentence( string )
# ------------------------------------------------------------------------------
# [1] A sentence.
# ------------------------------------------------------------------------------
# Returns the processed sentence (POS tagged/stopwords) and it's surface features.
# ------------------------------------------------------------------------------
def process_sentence(sentence):
    surfaceFeatures = Counter()
    
    # Extract surface features:
    sentence_length(surfaceFeatures, sentence)
    
    words = word_tokenize(sentence)
    taggedSentence = nltk.pos_tag(words)
    processedSentence = [ w for w in taggedSentence if w[0] not in stopwords ] 
    # Alternatively:
    # cleanedSentence = [ w for w in taggedSentence if w[0] not in stopwords and w[1] in ['NN', 'JJ', 'NNP'] ]

    return processedSentence, surfaceFeatures


# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# EXTRACT SURFACE FEATURES:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

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
        c.update({ "SF_LENGTH_1" : 1.0 })
    elif l <= 20:
        c.update({ "SF_LENGTH_2" : 1.0 })
    elif l <= 30:
        c.update({ "SF_LENGTH_3" : 1.0 })
    else:
        c.update({ "SF_LENGTH_4" : 1.0 })

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













