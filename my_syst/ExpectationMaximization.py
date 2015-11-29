__author__ = 'Robin Joganah'

# !/usr/bin/env python

from sklearn.feature_extraction.text import CountVectorizer
import nltk
import numpy as np
import random as rnd


class ExpectationMaximization:
    def __init__(self,data=[]):
        
        self.p_d,self.p_d_s_c,self.p_c,self.p_c_s_d = [],[],[],[]
        if(data):
            self.data = [i[0] for i in data]
            self.score = [i[1] for i in data]
            self.feedback = [i[2] for i in data]
  
        
    def distEuclid(self,vecA,vecB):
        return np.linalg.norm(vecA-vecB)


    def pre_traitement(self):
        data =  self.data
        self.vectorizer = CountVectorizer()
        self.X = self.vectorizer.fit_transform(data)
        self.X_data = [0] * self.X.shape[1]
        self.X_array = self.X.toarray()
        for document in self.X.toarray():
            self.X_data = self.X_data + document
        self.vocabulary_size = len(self.X_data)
        self.n_tokens = np.sum(self.X_data)


    def generate_cluster(self):
        bornes = [(max(self.X_array[:,i]),min(self.X_array[:,i])) for i in self.X_array[1]]
        return [rnd.uniform(min_v,max_v) for max_v,min_v in bornes]


    def expectation_maximization(self,k=3):
        data = self.data
        self.pre_traitement()
        self.liste_cluster = [self.generate_cluster() for i in range(k)]

        for document in data:
            prob_results = [self.prob_generer_mots(word) for word in nltk.word_tokenize(document) ]
            self.p_d.append(np.product(prob_results))
            self.p_d_s_c.append(self.proba_d_s_c(self.X_array[data.index(document)],self.liste_cluster))
        self.p_d_s_c = np.array(self.p_d_s_c)

        for cluster in self.liste_cluster:
            index = self.liste_cluster.index(cluster)
            self.p_c.append(np.sum(self.p_d_s_c[:,index])/ len(self.p_d_s_c[:,index]) )
            
        for i in range(len(data)):
            for j in range(k):
                print i,j
                print self.p_d[i],self.p_c[j],self.p_d_s_c[i][j]
                self.p_c_s_d.append(self.proba_c_s_d(self.p_d[i],self.p_c[j],self.p_d_s_c[i][j]))
                
        self.p_c_s_d = [element * 1.0 / np.sum(self.p_c_s_d) for element in self.p_c_s_d]
        self.recalcul_centroides()
        
    def recalcul_centroides(self):
        print self.p_c_s_d
        apport_pondere = [self.p_c_s_d[i] * self.data[i] for i in range(len(self.data))]
        return sum(apport_pondere,axis=0)
    
    
    def feedback_updata(self):
        return ""


    def proba_d_s_c(self,d,c):
        liste_distance = [self.distEuclid(d,c[cluster_index]) for cluster_index in range(len(c))]
        liste_distance =  [liste_distance[index] * 1.0 / np.sum(liste_distance) for index in range(len(liste_distance))]
        return np.array(liste_distance)


    def proba_c_s_d(self,p_d,p_c,p_d_s_c):
        return p_d * p_d_s_c / p_c


    def prob_generer_mots(self, mot):
        index = self.vectorizer.vocabulary_.get(mot)
        if (index):
            #Le mot est dans le vocabulaire
            return (self.X_data[index] * 1.0 + 1) / (self.vocabulary_size + self.n_tokens)
        else:
            #Mot inconnu du vocabulaire
            return 1 * 1.0 / (self.vocabulary_size + self.n_tokens)

    