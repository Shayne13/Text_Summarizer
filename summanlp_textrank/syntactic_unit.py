
# class SyntacticUnit(object):

#     def __init__(self, text, label, index, token=None, processed=None, tag=None):
#         self.text = text
#         self.processed = processed
#         self.token = token
#         self.label = label
#         self.index = index
#         self.score = -1
#         self.tag = tag[:2] if tag else None # just first two letters of tag

#     def __str__(self):
#         return u'Original Text: ' + self.text.encode('utf-8')

#         # return u'Original Text: ' + self.text + u'\n'
#         # return u"Original Text: '" + self.text + "'\n" + \
#         # "Processed Text: '" + self.processed + "'\n" + \
#         # "Label, Index, Score: '" + self.label + "', " + self.index + ", " + str(self.score)

#     def __repr__(self):
#         return str(self)

class WordUnit(object):

  def __init__(self, text, token=None, tag=None):
    self.text = text
    self.token = token
    self.score = -1
    self.tag = tag[:2] if tag else None # just first two letters of tag

  def __str__(self):
    return u'Original Text: ' + self.text.encode('utf-8')

    # return u'Original Text: ' + self.text + u'\n'
    # return u"Original Text: '" + self.text + "'\n" + \
    # "Processed Text: '" + self.processed + "'\n" + \
    # "Label, Index, Score: '" + self.label + "', " + self.index + ", " + str(self.score)

  def __repr__(self):
    return str(self)