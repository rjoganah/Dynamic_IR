'''
Created on 2015-05-06

@author: Robin Joganah
'''

import random

class Combine:
    def __init__(self,docs_lda,docs_solr,docs_kmeans,docsSubmittedID,contribution_alg = (0.49,0.255,0.255)):
        self.docs_lda = docs_lda
        self.docs_solr = docs_solr
        self.docs_kmeans = docs_kmeans
        self.contribution_alg = contribution_alg
        self.docsSubmittedID = docsSubmittedID

    def P(self):
        return 1
        # self.temp_explore = 0.9 * self.temp_explore 
        # #Exponentielle negative, si le chemin est vraiment tres mauvais, il a peu de probabilites d etre pris dans le recuit simule
        # return math.exp( -abs((self.nb_topics_trouve / self.nb_topics_min) - (self.nb_topics_min_prec / self.nb_topics_trouve_prec))/self.temp_explore  )
    def getNbTopics(self,feedback):
        self.nb_topics_trouve = len([key for key in feedback.iterkeys()])
        if self.nb_topics_trouve > 0:
            subtopic_ids = [key in feedback.iterkeys()]
            for subtopic in subtopic_ids:
                if(subtopic[-2] != '.'):
                    no_subtopic = subtopic[-2] + subtopic[-1]
                else:
                    no_subtopic = subtopic[-1]
                if(int(no_subtopic) > self.nb_topics_min):
                    self.nb_topics_min = no_subtopic
    def updateTemp(self):
        self.temp_explore = 0.2 * self.temp_explore

    
        
    def run(self):
        docs_lda,docs_kmeans,docs_solr = self.docs_lda,self.docs_kmeans,self.docs_solr
#         print 'lda',docs_lda
#         print 'kmeans',docs_kmeans
#         print 'solr',docs_solr
        contribution_alg = self.contribution_alg
        list_docs = {}
        list_docs_score = []
        # self.getNbTopics()
        if random.random() < self.P():
            # print 'explore'
            for doc in docs_lda:
                if doc in list_docs.iterkeys():
                    list_docs[doc][1] += contribution_alg[1]
                else:
                    list_docs[doc] = [0,contribution_alg[1],0]

            for doc in docs_kmeans:
                if doc in list_docs.iterkeys():
                    list_docs[doc][2] += contribution_alg[2]
                else:
                    list_docs[doc] = [0,0,contribution_alg[2]]

            for doc in docs_solr:
                if doc in list_docs.iterkeys():
                    list_docs[doc][0] += contribution_alg[0]
                else:
                    list_docs[doc] = [contribution_alg[0],0,0]
            for key in list_docs.iterkeys():
                score = list_docs[key][0] + list_docs[key][1] + list_docs[key][2]
                list_docs_score.append((key,score))
            list_docs_score = sorted(list_docs_score,key=lambda value:value[1],reverse=True)
            # print list_docs_score
            # print [doc[0] for doc in list_docs_score]
#             list_docs_score = [doc for doc in list_docs_score if doc[0] not in self.docsSubmittedID]
            
            return [doc[0] for doc in list_docs_score][0:5]
        else:
            return []

if __name__ == '__main__':
    docs_lda = ['1','2','3','4','7','8']
    docs_solr = ['4','5','6','1','2','8']
    docs_kmeans = ['7','2','1','6','8']
    docsSubmittedID = ['9','1','10','11','12','7','5','2']
    combine_instance = Combine(docs_lda,docs_solr,docs_kmeans,docsSubmittedID,contribution_alg = (0.49,0.255,0.255))
    print combine_instance.run()