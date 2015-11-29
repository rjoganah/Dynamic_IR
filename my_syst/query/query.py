'''
Created on 2015-09-10

@author: robinjoganah
'''
import my_syst.preprocessing.parse_xml as pxml
import re
import nltk
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import os

class Query(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.query = None
        self.raw_query = None
        self.domain_name = None
        self.dict_query_domain = pxml.create_dict_query_domain()
        self.map_name_domaine = {'Local_Politics' : 'local politics', 'Ebola' : 'ebola', 'Illicit_Goods' : 'hacking' }
        
    def process_query(self,query):
        
        self.domain_name = self.map_name_domaine[self.dict_query_domain[query]]
        query = re.sub(r'[^\w]', ' ', query)
        query = nltk.word_tokenize(query)
        if(self.domain_name):
            query = [pxml.stem_and_lemmatize(word) for word in query]
        query = ' '.join(query)
        self.raw_query = query
        self.query = query
        

class QueryIdfWeight(Query):
    '''
    classdocs
    '''
    

    def __init__(self):
        '''
        Constructor
        '''
        super(QueryIdfWeight,self).__init__()
        with open(self.path + "/tf_idf_" + "local_politics2" + ".p", "rb") as input_file:
                self.tf_idf_vectorizer_local_politics = pickle.load(input_file)
        with open(self.path + "/tf_idf_" + 'ebola'+ ".p", "rb") as input_file:
                self.tf_idf_vectorizer_ebola = pickle.load(input_file)
        with open(self.path + "/tf_idf_" + 'hacking'+ ".p", "rb") as input_file:
                self.tf_idf_vectorizer_hacking = pickle.load(input_file)
    
    def process_query(self,query):
         
        self.domain_name = self.map_name_domaine[self.dict_query_domain[query]]
        query_formatted = self.format_query(query)
        new_query = ' '.join(query_formatted)
        self.raw_query = new_query
        new_query = self.vectorize_and_transform(new_query)
        self.query = new_query
        
    def update_processed_query(self,new_query):
        new_query = self.vectorize_and_transform(new_query)
        self.query = new_query
        
    def format_query(self,query):
        query = re.sub(r'[^\w]', ' ', query)
        query = nltk.word_tokenize(query.lower())
        query = [pxml.stem_and_lemmatize(word) for word in query]
        return query
    
    def vectorize_and_transform(self,query):
        switcher = {
        'local politics': self.tf_idf_vectorizer_local_politics,
        'ebola': self.tf_idf_vectorizer_ebola,
        'hacking': self.tf_idf_vectorizer_hacking,
        }
        tf_idf_vectorizer = switcher.get(self.domain_name,None)
        query_vectorized = tf_idf_vectorizer.transform([query])
#         self.print_tf_idf_words(tf_idf_vectorizer,query_vectorized)
        new_query = ' '.join(self.get_tf_idf_words(tf_idf_vectorizer,query_vectorized))
        return new_query
        
    def print_tf_idf_words(self,tf_idf_vector,document):
        feature_names = tf_idf_vector.get_feature_names()
        for col in document.nonzero()[1]:
            print feature_names[col] + '^' + str(self.truncate(document[0, col],2))
            
    def get_tf_idf_words(self,tf_idf_vector,document):
        feature_names = tf_idf_vector.get_feature_names()
        tf_idf_words = [feature_names[col] + '^' + str(self.truncate(1 + document[0, col],2)) if feature_names[col] in nltk.word_tokenize(self.raw_query)\
                        else feature_names[col] + '^' + str(self.truncate(document[0, col],2)) for col in document.nonzero()[1]]
        return tf_idf_words
    
    def truncate(self,f, n):
        '''Truncates/pads a float f to n decimal places without rounding'''
        s = '%.12f' % f
        i, p, d = s.partition('.')
        return '.'.join([i, (d+'0'*n)[:n]])

if __name__ == '__main__':
    query_id_weight = QueryIdfWeight()
    query_id_weight.process_query("Spamming can be helpful")
#     query_id_weight.process_query("White Supremacists in Washington State")
#     query_id_weight.process_query("Ebola Orphans in Guinea, Liberia and Sierra Leone")
    print query_id_weight.query
    print query_id_weight.domain_name
    print query_id_weight.raw_query