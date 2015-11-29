from my_syst.query_expansion.search_algorithms import SearchAlgorithms
import pysolr
import solr
from scipy.sparse import csr_matrix
from scipy.sparse import coo_matrix
import nltk
import logging
from nltk.corpus import stopwords
import random
from search_algorithms.combine import Combine
from exploitation_exploration.diversification import get_rand_doc_from_list,NErecognition
from nltk.stem import PorterStemmer
from preprocessing.parse_xml import load_list_words_english_frequent,lemmatize
import re
# -*- coding: utf-8 -*-


class DocumentObject(object):
    """ 
    Document object to store data from each documents
    Public attributes:
    - key : unique key of the document
    - text : content of the text document
    - vector : vectorized sparse matrix of the text
    - solr_score : score from solr search engine
    """
    def __init__(self,key,text,vector,solr_score):
        self.key = key
        self.text = text
        self.vector = vector
        self.solr_score = solr_score

class DocStore(object):
    """ 
    Keep track of all docs stored during the session
    """
    def __init__(self):
        self.docsList = []
    def addDoc(self,doc):
        self.docsList.append(doc)

class DocStoreCombination(object):
    """ 
    Keep track of all docs stored during the session
    """
    def __init__(self):
        self.docsList = {}
    def addDoc(self,doc):
        self.docsList.append(doc)

class Controller:
    
    def __init__(self,query,domain_name):
        self.docStore = DocStore()
        self.docsSubmittedID = []
        self.conn = solr.SolrConnection('http://localhost:8983/solr')
        self.solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
        logging.basicConfig(filename='example.log',level=logging.DEBUG)
        self.query = query
        self.nb_topics_trouve = 0
        self.nb_topics_min = 0
        self.turn_number = 1
        self.temp_explore = 1000
        self.domain_name = domain_name
        self.query_adapt = self.query_to_query_adapt(self.query, domain_name)
        # self.query_adapt = self.query_to_query_adapt_title(self.query,domain_name)
        self.data,self.docs_id = self.requete(self.query_adapt,20)
        self.search_instance = SearchAlgorithms(self.data,self.query)
        self.list_frequent_english_words = load_list_words_english_frequent()
        for i,dat in enumerate(self.data):
            doc = DocumentObject(self.docs_id[i],dat[0],self.search_instance.X[i],dat[1])
            self.docStore.addDoc(doc)

            


        
    def delete_all_docs(self):
        """
        Delete all docs from the solr connection
        """
        self.solr.delete(q='*:*')
    
    def new_turn(self,updated_query,turnNumber,nbDocs = 20):
        new_data = []
        new_docs_id = []
        self.turn_number = turnNumber
        self.docStore = DocStore()
        self.query_adapt = self.query_to_query_adapt(updated_query, self.domain_name)
        self.data,self.docs_id = self.requete(self.query_adapt, nbDocs + turnNumber*5 )
        
        for i,dat in enumerate(self.data):
            if (self.docs_id[i] not in self.docsSubmittedID):
                new_data.append(dat)
                new_docs_id.append(self.docs_id[i])
        self.data = new_data[0:nbDocs]
        self.docs_id = new_docs_id[0:nbDocs]
        self.search_instance = SearchAlgorithms(self.data,updated_query)
        for i,dat in enumerate(self.data):
            doc = DocumentObject(self.docs_id[i],dat[0],self.search_instance.X[i],dat[1])
            self.docStore.addDoc(doc)
        if(len(self.docStore.docsList) < 5):
            raise ValueError('Not enough docs')
        
    def requete(self,q,nbrows = 25,start = 0):
        """ 
        Try to query the solr client
        Args:
        - q : is the query
        - nbrows : is the number of result returned
        """
        response = self.conn.query( q + ' fl=*,score',rows = nbrows,start = start)
        return [(hit['title'][0] + ' ' + hit['content'][0],hit['score'],[])\
                 for hit in response.results],[hit['id'] for hit in response.results]

    def run_combine(self,docs_lda,docs_kmeans,docs_solr,poids = (0.49,0.255,0.255)):
        combine = Combine(docs_lda = docs_lda,\
                           docs_kmeans = docs_kmeans,\
                            docs_solr = docs_solr,\
                            contribution_alg = poids,\
                            docsSubmittedID = self.docsSubmittedID)
        return combine.run()

    def exploit(self,topic_id):
        print 'exploit'
        raise NotImplementedError
        
    def search_solr(self,query):
        """ Controller of solr query
        return data from the search
        """
        data,docs_id = self.requete(query, 25)
        return data,docs_id
    
    def new_req_random_doc(self):
        _doc_id = get_rand_doc_from_list()
        rd_nb = random.randrange(25,50)
        data,_id_doc = self.requete(q=self.query,nbrows =100,start = rd_nb)
        data = re.sub(r'[^\w]', ' ', data[0][0])
        data =  nltk.word_tokenize(data)
        vect_doc_transformed = self.search_instance.tfidf_vect.transform(data)
        cx = csr_matrix(vect_doc_transformed)
        cx = coo_matrix(cx)
        values = []
        for _i,j,v in zip(cx.row, cx.col, cx.data):
            values.append((self.search_instance.tfidf_vect.get_feature_names()[j],v))
            new_query = sorted(values,key=lambda value:value[1],reverse=True)

        words_present_other_docs= [words[0] for words in new_query]
        words_soustraction = list(set([word for word in data if word not in words_present_other_docs and word not in self.list_frequent_english_words ]))
        print 'len words_data',len(data)
        print 'len words_soustraction',len(words_soustraction)
        tokens = nltk.word_tokenize(' '.join(NErecognition(' '.join(data))))
        tokens = list(set(tokens))
        print len(tokens),tokens
        stemmer = PorterStemmer()
        list_words = [token for token in tokens if stemmer.stem(lemmatize(token.lower())) not in self.list_frequent_english_words[0:1000]]
        words_selected = []
        if len(list_words)>20:
            nb_words = 20
        else : nb_words = len(list_words)
        for _i in range(nb_words):
            rd_word = random.choice(list_words)
            list_words.pop(list_words.index(rd_word))
            words_selected.append(rd_word)
        query =  ' '.join(words_selected) +' '+ self.query
        print 'Random Query'
        if len(query)==0:
            query = ' '.join(data)
        query = self.query_to_query_adapt(query,self.domain_name)
        print query
        data,ids=self.requete(query,100)
        roc = SearchAlgorithms(data,query)
        docs_kmean = roc.kmeans_centroide()
        docs_cluster = [doc[0] for doc in docs_kmean if len(doc)>0]
        docs_cluster += [doc[1] for doc in docs_kmean if len(doc)>1]
        docs_cluster_id = [ids[doc[0]] for doc in docs_cluster]
        list_docs_to_submit = [doc for doc in docs_cluster_id if doc not in self.docsSubmittedID]
        return list_docs_to_submit[0:5]

    def run_rocchio(self,data,docs_id,rel,non_rel,nbWordsAdd = 4,posT = True):
        """
        Launch rocchio algorithm on data to calculate the new query from
        given relevant and non-relevant docs
        Args:
        - non_rel : non relevant documents
        - rel : relevants documents
        - query_words : words from the intial query
        - query_adapt : query formated for the search
        """
        # data,docs_id = self.data,self.docs_id
        pos = posT
        search_instance = self.search_instance
        id_rel_docs = []
        for _i,rel_doc in enumerate(rel):
            for j,doc_id in enumerate(docs_id):
                if(rel_doc == doc_id):
                    id_rel_docs.append(j)
        id_non_rel_docs = []
        for _i,non_rel_doc in enumerate(non_rel):
            for j,doc_id in enumerate(docs_id):
                if(non_rel_doc == doc_id):
                    id_non_rel_docs.append(j) 
        rel = [search_instance.X_tfidfVect[i].todense() for i,_dat in enumerate(data) if i in id_rel_docs ]
        non_rel = [search_instance.X_tfidfVect[i].todense() for i,_dat in enumerate(data) if i in id_non_rel_docs]

        if(len(rel) == 0):

            new_query = search_instance.rocchio_algorithm(search_instance.query_vector.todense(), non_rel, rel)
            cx = csr_matrix(new_query)
            cx = coo_matrix(cx)
            values = []
            for i,j,v in zip(cx.row, cx.col, cx.data):
                values.append((search_instance.tfidf_vect.get_feature_names()[j],v))
                new_query = sorted(values,key=lambda value:value[1],reverse=True)
            new_words = [word for word,_score in new_query[0:30] if word not in self.query.lower().split()]
            if len(new_words) == 0:
                return self.query
            if(pos):
                return self.query + ' ' + ' '.join(new_words[0:nbWordsAdd])
            else:
                return self.query +' NOT(' +' '.join(new_words[0:nbWordsAdd])+ ')'
        else:
    
            new_query = search_instance.rocchio_algorithm(search_instance.query_vector.todense(), rel, non_rel)
            cx = csr_matrix(new_query)
            cx = coo_matrix(cx)
            values = []
            for i,j,v in zip(cx.row, cx.col, cx.data):
                values.append((search_instance.tfidf_vect.get_feature_names()[j],v))
                new_query = sorted(values,key=lambda value:value[1],reverse=True)

            new_words = [word for word,_score in new_query[0:30] if word not in self.query.lower().split()]
        if (pos):
            return ( self.query + ' ' +  ' '.join(new_words[0:nbWordsAdd]) )
        return ( self.query + ' NOT(' +  ' '.join(new_words[0:nbWordsAdd]) + ')')
    
    def run_kmeans(self):
        """Run the search and keep n (20) results perform kmeans over these results with 5 clusters
        Args:
        - query : query words to perform the search
        Returns:
        Most similar document for each cluster
        """
        _data,docs_id = self.data,self.docs_id
        roc = self.search_instance
        docs_kmean = roc.kmeans_centroide()
        # docs_cluster = [doc[0] for doc in docs_kmean]
        # docs_cluster_id = [docs_id[doc[0]] for doc in docs_cluster]
        docs_cluster = [doc[0] for doc in docs_kmean if len(doc)>0]
        docs_cluster += [doc[1] for doc in docs_kmean if len(doc)>1]
        docs_cluster += [doc[2] for doc in docs_kmean if len(doc)>2]
        docs_cluster += [doc[3] for doc in docs_kmean if len(doc)>3]
        docs_cluster += [doc[4] for doc in docs_kmean if len(doc)>4]
        docs_cluster += [doc[5] for doc in docs_kmean if len(doc)>5]
        docs_cluster += [doc[6] for doc in docs_kmean if len(doc)>6]
        docs_cluster_id = [docs_id[doc[0]] for doc in docs_cluster]
        return docs_cluster_id[0:5]
    
    def run_kmeans_solr(self,pageNumber=0):
        """Run the search and keep n (50) results perform kmeans over these results with 5 clusters
        Args:
        - query : query words to perform the search
        Returns:
        Most similar document for each cluster
        """
        roc = self.search_instance
        docs = roc.kmeans_solr()
        top5Docs = []
        for key in docs.iterkeys():
            docs[key] = sorted(docs[key], key = lambda value:value[1],reverse=True)
            top5Docs.append(docs[key][pageNumber])
        return top5Docs
    
    
    def clean_stopwords(self,text):
        """ Util function to clean a text
        Args:
        - text: text to clean
        Returns:
        Text without stopwords
        """
        stop_words = stopwords.words('english')
        tokens = nltk.word_tokenize(text)
        good_words = [w for w in tokens if (w not in stop_words)]
        return ' '.join(good_words)
    
    
    def run_lda(self,nbTopics = 5,nbWords=5):
        """Run the search and keep n (50) results perform LDA over these results with 5 topics
        Args:
        - query : query words to perform the search
        Returns:
        Most similar document for each cluster
        """
        docs = []
        roc = self.search_instance
        _docs_lda,word_topics = roc.lda(nb_topics = nbTopics)
        words = {}
        for i,topic in enumerate(word_topics):
            for word in topic:
                if word.lower() not in nltk.word_tokenize(self.query.lower()):
                    if i not in words:
                        words[i] = [word]
                    else:
                        words[i].append(word)
        new_queries = [self.query + ' ' + ' '.join(words[i][0:nbWords]) if i in words else self.query for i,_x in enumerate(word_topics)]
        print "lda queries"
        print new_queries
        print "/lda queries"
        results_lda = [self.requete(self.query_to_query_adapt(new_query,self.domain_name),10) for new_query in new_queries]
        docs_to_submit = [result[1] for result in results_lda if(result[1][0])]
        for doc_list in docs_to_submit:
            for doc in doc_list:
                if(doc not in self.docsSubmittedID):
                    self.docsSubmittedID.append(doc)
                    docs.append(doc)
                    break
        return docs
    
    
    def query_to_query_adapt(self,query,domain_name):
        return 'subject:(' + domain_name + ')' + ' AND content:(' + query + ') '

            
    def query_to_query_adapt_title(self,query,domain_name):
        return 'subject:(' + domain_name + ')' + ' AND (content:((' + query + ') OR subject:(' + domain_name + ')' + ' AND title:(' + query + ')))'

        
        
    def run_lda_solr(self):
        """Run the search and keep n (50) results perform LDA over these results with 5 topics
        Args:
        - query : query words to perform the search
        Returns:
        For each topic pick the best result according to the SolR score
        """
        data,docs_id = self.data,self.docs_id
        roc = self.search_instance
        docs_lda,_word_topics = roc.lda()
        top_5_lda = [docs[0] for docs in docs_lda]
        top_5_lda = sorted(top_5_lda, key =lambda value:value[1], reverse = True )
        _top_5_lda_txt = [data[doc[0]] for doc in top_5_lda]
        docs = [docs_id[doc[0]] for doc in top_5_lda]
        return docs


if __name__ == '__main__':
    """
    main to test functions
    """
    # text = "Fatalities and Injuries" 
    # query = "Columbia-Snake salmon dam controversery"
    query = "Community Care Centers"
    
    # query_adapt = 'subject:(local politics)content:(Columbia-Snake salmon dam controversery)'.lower()
    query_adapt = 'subject:(ebola) AND (content:(community care center) OR title:(community care center))'
    # controller = Controller(query,"local politics")
    controller = Controller(query,"ebola")
    # print controller.clean_stopwords(text)
    # docs = controller.run_kmeans()
    # print "Kmeans",docs
    # docs = controller.run_lda(nbTopics = 5)
    # print "LDA",len(docs),docs
    # docs = controller.run_lda_solr()
    # print "LDA_solr",docs
    # data = []
    # rel = [u'1366485246-1fe11fd5375119ae999c35a49a903ea8', u'1320589740-abe5789d7b6de58979e123c1818380a5', u'1349474584-d7df60adad1cf42bf6e4d9cf95207327', u'1343043010-9ed8949950c927e70383f8f09d2d4cae', u'1335646200-f9a224e035bd04133d428265229bc65c']
    # non_rel = []
    # new_query = controller.run_rocchio(controller.data,controller.docs_id,rel,non_rel)
    # print new_query
    # rel = [u'1320589740-abe5789d7b6de58979e123c1818380a5']
    # non_rel = [u'1366485246-1fe11fd5375119ae999c35a49a903ea8', u'1349474584-d7df60adad1cf42bf6e4d9cf95207327', u'1343043010-9ed8949950c927e70383f8f09d2d4cae', u'1335646200-f9a224e035bd04133d428265229bc65c']
    # new_query = controller.run_rocchio(controller.data,controller.docs_id,rel,non_rel)
    # print new_query
    # docs = controller.run_kmeans_solr()
    # controller.search_instance.mixtureAlg()
    # docs_solr = [doc.key for doc in controller.docStore.docsList[0:10]]
    # docs_kmean = controller.run_kmeans()
    # docs_lda = controller.run_lda()
    # docs = controller.run_combine(docs_lda,docs_kmean,docs_solr)
    print controller.new_req_random_doc()
     

    # print docs    
    