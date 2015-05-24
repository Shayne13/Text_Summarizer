#!/usr/bin/env python

from parser import *

# Arg Check:
# ------------------------------------
if len(sys.argv) != 4:
  sys.exit('''Please pass in the following arguments:
1. The folder of xml files to be parsed.
2. The output folder for gold summaries.
3. The output folder for parsed training files.''')

inputXML = sys.argv[1]
outputGold = sys.argv[2]
outputXML = sys.argv[3]

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# TRAIN:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

parse_folder(inputXML, outputGold, 0)
allSentences, allSurfaceFeatures = parse_folder(inputXML, outputXML, 1)

print allSentences[0][0]



# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# RANDOM NOTES:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# import script as though it is a module to run functions from it.
# s = f('summary')
# s.text()
# len(s)
# dir(s)
# type(s)