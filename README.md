# Text_Summarizer

Git Commands:
--------------
git pull
git add -A
git commit -m "First Commit"
git push
--------------

Download:
--------------
1. Dataset
2. ROUGE
3. pyquery (xml parsing)
4. nltk (word tokenization)
5. [pandas](http://pandas.pydata.org/) - ashkonf_pagerank
6. NetworkX (for textrank)
--------------

Files:
--------------
1. DIVIDE DATA
2. PARSER
3. ...
4. TEXTRANK
5. ashkonf_pagerank
6. timothyasp_pagerank
1. wordentail (from class)
2. distributedwordreps.py (from class)
--------------

File Format:
-------------
    #!/usr/bin/env python
    # ------------------------------------
    # Args:
        [1] file.txt
        [2] flag: [1, 3]
    # EG: python example.py test.txt 1
    # ------------------------------------
    # Description ...
    # ------------------------------------
-------------

# Additional Imports (for later use):
# ------------------------------------
import os
import sys
import csv
import copy
import random
import pickle
import itertools
from operator import itemgetter
from collections import defaultdict
# ------------------------------------
import numpy as np
import scipy
import scipy.spatial.distance
import sklearn.metrics
from numpy.linalg import svd
from collections import defaultdict
# ------------------------------------
#!/bin/bash


Useful shit:
http://kavita-ganesan.com/rouge-howto
Check for a module's installation path: 
perldoc -l XML::DOM

TO RUN ROUGE:
perl ROUGE-1.5.5.pl -e data -f A -a -x -s -m -2 -4 -u text_summarizer/settings.xml



