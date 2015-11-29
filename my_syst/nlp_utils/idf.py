'''
Created on 2015-09-08

@author: robinjoganah
'''

import nltk
from my_syst.preprocessing import parse_xml
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

def tokenize(text):
    tokens = nltk.word_tokenize(text)
#     stems = [parse_xml.stem_and_lemmatize(token).lower() for token in tokens]
    return tokens
        
#this can take some time
def transform_tf_idf(text,domain):
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
    tfs = tfidf.fit_transform(text)
    return tfidf

def print_tf_idf_words(tf_idf_vector,document):
    feature_names = tf_idf_vector.get_feature_names()
    for col in document.nonzero()[1]:
        print feature_names[col], ' - ', document[0, col]
if __name__ == '__main__':
    datas = ['ebola is the main virus', 'ebola in sierra leone', 'ebola is the most important virus in liberia', 'ebola disapeared in Nigeria']
    tf_idf_vector = transform_tf_idf(datas, 'ebola_test')
    document = tf_idf_vector.transform([datas[0]])
    print document
    print_tf_idf_words(tf_idf_vector, document)