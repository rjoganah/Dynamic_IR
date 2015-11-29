'''
Created on 2015-09-03

@author: robinjoganah
'''
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
from nltk.corpus import stopwords
import nltk

class Collocations(object):
    '''
    classdocs
    '''


    def __init__(self, corpus):
        '''
        Constructor
        '''
        self.stopwords_ = set(stopwords.words('english'))
        self.corpus = corpus
        
        
    def collaction_discovery(self):
        self.corpus = nltk.word_tokenize(self.corpus.lower())
        bigramm_finder = BigramCollocationFinder.from_words(self.corpus)
        filter_bigram = lambda w:len(w)<3 or w in self.stopwords_
        bigramm_finder.apply_word_filter(filter_bigram)
        top_10_bigrams = bigramm_finder.nbest(BigramAssocMeasures.likelihood_ratio,10)
        return top_10_bigrams



if __name__ == '__main__':
    colloc_big = Collocations('Marvel studio is the best studio for science-fiction movies Marvel studio is clearly the leader in this industry but Pixar studio are quite good in animation movies Pixar studio but not in science-fiction')
    print colloc_big.collaction_discovery()