from parser import *

from wordentail import sklearn
from sklearn.feature_selection import RFE
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectFpr, chi2
from sklearn.linear_model import LogisticRegression
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import cross_val_score
from sklearn import metrics

inputXML = "sample_rawdata"
outputGold = "sample_gold"
outputXML = "sample_train"

# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# TRAIN:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

summaries, summaryFeatures = parse_folder(inputXML, outputGold, 0)
allSentences, allSurfaceFeatures = parse_folder(inputXML, outputXML, 1)

# LABELS = ['SUMMARY', 'BODY']
# vectorizer = DictVectorizer(sparse=False)
# X = vectorizer.fit_transform(feats)



# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# RANDOM NOTES:
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# import script as though it is a module to run functions from it.
# s = f('summary')
# s.text()
# len(s)
# dir(s)
# type(s)