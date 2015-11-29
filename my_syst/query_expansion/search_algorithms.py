'''
Created on 2015-05-06

@author: Robin Joganah
'''
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import mixture
import numpy as np
from nltk.corpus import stopwords
import nltk
import lda


class SearchAlgorithms:
    def __init__(self,data =[],query =""):
        if query:
            self.query = query
        if data:
            self.data = [i[0] for i in data]
            self.score = [i[1] for i in data]
            self.feedback = [i[2] for i in data]
            self.preprocess()
        
        
    def distEuclid(self,vecA,vecB):
        """ 
        Euclidian distance between 2 vectors
        Args :
        -vecA : first vector
        -vecB : second vector
        Return:
        Distance between vector A and B
        """
        return np.linalg.norm(vecA-vecB)
        
    def rocchio_algorithm(self,query,relev_documents,non_relev_documents,alpha = 1, beta = 0.75, gamma = 0.25):
        """ 
        Run rocchio algorithms over relevants and non relevants documents with the initial query vector to compute a new query vector
        Args :
        -query : query vector
        -relev_documents : relevants document list
        -non_relev_documents : non_relevants documents list
        -alpha : rocchio coef for query vector
        -beta : rocchio coef for relevants docs
        -gamma : rocchio coef for non_relevants docs
        Return:
        New query vector
        """
        new_query = alpha * query
        relev_vector = np.sum(relev_documents,axis=0) / len(relev_documents)
        if (len(non_relev_documents) > 0):                       
            non_relev_vector = np.sum(non_relev_documents, axis=0) / len(non_relev_documents)
            new_query = new_query + beta * relev_vector - gamma*non_relev_vector
        else :
            new_query = new_query + beta * relev_vector
        return new_query
    
    
    def MMR(self,doc_compare,docs_a_comparer):
        lamb = 0.1
        values = [(i,self.distEuclid(doc_compare[1].todense(),doc_to_compare[1].todense()))\
                   for i,doc_to_compare in enumerate(docs_a_comparer)]
        values = [(i,lamb * doc[0][1] - (1-lamb) * values[i][1]) for i,doc in enumerate(docs_a_comparer)]
        sorted_val = sorted(values,key=lambda value:value[1],reverse=False)
        maxi = np.argmax(values,axis=1)
        print self.data[docs_a_comparer[maxi[0]][0][0]]
        print sorted_val
        

    def lda(self,nb_topics = 5,nbWords = 10):
        model = lda.LDA(n_topics=nb_topics, n_iter=100, random_state=1)
        X = self.X
        model.fit(X)
        topic_word = model.topic_word_
        topics_words = []
        n_top_words = nbWords + 1
        word_list_per_topic = []
        for i, topic_dist in enumerate(topic_word):
            topic_words = np.array(self.vocabulary)[np.argsort(topic_dist)][:-n_top_words:-1]
            word_list_per_topic.append(topic_words)
            topics_words += topic_words
            # print('Topic {}: {}'.format(i, ' '.join(topic_words)))
        doc_topic = model.doc_topic_ 
        topic_list = []
        for i in range(0,nb_topics):
            topic_list.append([])
        for i,topics in enumerate(doc_topic):
            index = topics.argmax()
            topic_list[index].append((i,topics[index]))
        for i,topics in enumerate(topic_list):
            topics = sorted(topics,key=lambda value:value[1],reverse=True)
            topic_list[i] = topics[0:5]
        return topic_list,word_list_per_topic


    def mixtureAlg(self,nb_comp = 5):
        g = mixture.DPGMM(n_components = 2)
        g.fit(self.X.todense())
        print g.predict(self.X.todense())
        pred =  g.score(self.X.todense(),y=0)
        print pred
        print np.sum(pred)

    def tokenize(self,text):
        try:
            tokens = nltk.word_tokenize(text.encode('utf-8'))
        except UnicodeDecodeError:
            tokens = nltk.word_tokenize(text)
        stems = []
        for item in tokens:
            stems.append(item.lower())
            # stems.append(PorterStemmer().stem(item.lower()))
        return ' '.join(stems)

    def preprocess(self):
        count_vect = CountVectorizer(stop_words='english')
        tokens = [self.tokenize(line) for line in self.data]
        count_vect.fit(tokens)
        self.count_vect = count_vect
        self.tfidf_vect = TfidfVectorizer(stop_words='english')
        self.tfidf_vect.fit(tokens)
        self.X_tfidfVect = self.tfidf_vect.transform(tokens)
        X_train_counts = count_vect.transform(tokens)
        self.X = X_train_counts
        tf_transformer = TfidfTransformer()
        tf_transformer.fit(X_train_counts)
        X_train_counts = tf_transformer.transform(X_train_counts)
        self.tf_transformer = tf_transformer
        self.X_tfidf = X_train_counts
        self.query_vector = self.tfidf_vect.transform([self.tokenize(self.query)])
        voc = count_vect.vocabulary_
        self.vocabulary = [(v,k) for k, v in voc.iteritems()]
        sorted_voc = sorted(self.vocabulary,key=lambda value:value[0],reverse=False)
        self.vocabulary = [k for v,k in sorted_voc]
        
            
    def cluster_data(self,k=5):
        km = KMeans(n_clusters=k, init='k-means++', max_iter=1000, n_init=100,n_jobs=-1)
        X_train_counts = self.X_tfidfVect
        km.fit(X_train_counts[:-1])
        predicted = km.predict(X_train_counts)
        return predicted,X_train_counts,km
    
    
    def kmeans_solr(self):
        """
        List of docs ranked by the solr score in each cluster (Ex : docs 1 and 3 are part of cluster 1, doc 1 has a score of 0.23, doc 3 0.34, doc 3 will be ranked first)
        """
        classes, X,km = self.cluster_data()
        zipped_data = zip(classes,X,self.score)
        clusters_hier = {}
        for i,var in enumerate(zipped_data):
            if(var[0] in clusters_hier):
                clusters_hier[var[0]].append((i,var[2]))
            else:
                clusters_hier[var[0]] = [(i,var[2])]    
        return clusters_hier

        
        
    def kmeans_centroide(self):
        """
        List of docs ranked by distance with the centroid of their cluster
        """
        index_cluster = 0
        listCluster=[[]]
        classes, X,km = self.cluster_data()
        for i,center in  enumerate(km.cluster_centers_):
            if index_cluster!= 0:
                listCluster.append([])
            for index_class,elem in enumerate(X):
                if(index_cluster == classes[index_class]):
                    dist = self.distEuclid(center, elem)
                    listCluster[index_cluster].append((index_class,dist))
            index_cluster+=1
        for i in range(len(set(classes))):
            listCluster[i] = sorted(listCluster[i],key=lambda value:value[0],reverse=False)
        docs_to_return_kmean = listCluster
        return docs_to_return_kmean

    
    

        
                
        
       
        
    