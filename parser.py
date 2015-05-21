#!/usr/bin/env python

import sys, os
from pyquery import PyQuery as pq
# import csv
# import copy

# ------------------------------------
# Args: None
# EG:
# ------------------------------------
# Description ...
# ------------------------------------

# Arg Check:
# ------------------------------------
if len(sys.argv) != 2:
  sys.exit('''Please pass in the following arguments:
1. The folder of xml files to be parsed.''')

folder = sys.argv[1]
paths = [ "./{0}/{1}".format(folder, f) for f in os.listdir(folder) ]

for p in paths:
  f = pq(filename=p)
  s = f('summary')
  b = f('body')


# s = f('summary')
# s.text()
# len(s)
# dir(s)
# type(s)










