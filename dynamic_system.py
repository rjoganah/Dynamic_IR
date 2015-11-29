from __future__ import absolute_import
import argparse
from itertools import chain
import logging
import os
import random
import kvlayer
import yakonfig
from pprint import pprint
from trec_dd.harness.run import Harness
from trec_dd.harness.truth_data import parse_truth_data
from trec_dd.system.ambassador_cli import HarnessAmbassadorCLI
from my_syst.main import Controller
from my_syst.feedback_processing.FeedbackProcessing import FeedbackPocessing,FeedbackOptions
from multiprocessing import Pool
from run_cube_test import run_cubeTest
from my_syst.query.query import Query,QueryIdfWeight


logger = logging.getLogger(__name__)
logging.basicConfig(filename='log_follow.log',level=logging.DEBUG)
class SearchSystem(object):
    '''A ranking system that returns a random document id.
    '''
    
    def __init__(self, doc_store,method,options,poids):
        print "===========INIT================"
        self.doc_store = doc_store
        self.submitted_docs = set()
        self.feedbacks = {}
        self.current_topic = 0
        self.rel_docs = []
        self.non_rel_docs = []
        self.id_topic = 0
#         self.dict_query_domain = pxml.create_dict_query_domain()
        self.words_to_add = []
        self.feedback_options = options
        self.method = method
        self.poids = poids
        self.query = None
        self.domain_name = None
        self.new_query = None
        self.query_object = Query()
        self.allreadyHere = 0
        


 

    def search(self,query, page_number):
        '''Select 5 random documents.
        '''

        if page_number == 1:
            #Initialize variables for all pages for this topic
            self.new_query = None
            self.words_to_add = []
            self.id_topic += 1
            if(self.id_topic != 3):
                return []

            
#         elif(self.id_topic in self.feedbacks):
#             self.query_object.update_processed_query(self.new_query)
#             self.query = self.query_object.query
            
            self.query_object.process_query(query)
            self.domain_name = self.query_object.domain_name
            self.query = self.query_object.query
        
        method = self.method
        logging.info('QUERY informations : ' + ' '.join([self.query,\
                                                         self.domain_name,\
                                                         str(page_number),\
                                                         method]))        
        if(self.current_topic  == 0 or self.current_topic != self.id_topic ):  
            self.query = self.query.lower()
            self.controller = Controller(self.query,self.domain_name)
            self.current_topic = self.id_topic 
        if page_number == 1:
            if(self.domain_name):
                docs_static = self.run_search_static(method)
                print docs_static
                return docs_static
                
            else: return []
        if page_number > 2:
            if(self.id_topic not in self.feedbacks.iterkeys() and page_number < 1):
                self.docs = self.controller.new_req_random_doc()
                self.submitted_docs.update(self.docs)
                self.controller.docsSubmittedID = list(self.submitted_docs)
                return self.doc_ids_to_results(self.docs)
            else:
                return []
        if page_number >= 2:        
            if(self.id_topic in self.feedbacks.iterkeys() and page_number > 3):
                return []
            self.data = self.controller.data
            self.docs_id = self.controller.docs_id
            
            try:
                self.controller.new_turn(self.new_query,page_number)
            except ValueError:
#                 self.docs = self.controller.docStore.docsList[0:5]
                self.docs = [doc.key for doc in\
                              self.controller.docStore.docsList[0:5]]
                self.submitted_docs.update(self.docs)
                self.controller.docsSubmittedID = list(self.submitted_docs)
                return self.doc_ids_to_results(self.docs)
            
            self.data = self.controller.data
            self.docs_id = self.controller.docs_id
            return self.run_search_dynamic(method)

    
    
    def run_search_static(self,method):
        if(method == 'solr'):
            self.docs_solr = [doc.key for doc in\
                              self.controller.docStore.docsList[0:5]]
            self.docs = self.docs_solr[0:5]
        elif(method == 'kmeans'):
            self.docs_kmean = self.controller.run_kmeans()
            logging.info("========DOCS KMEAN==========")
            logging.info(str(self.docs_kmean))
            self.docs =  self.docs_kmean
        elif(method == 'lda'):
            self.docs_lda = self.controller.run_lda()
            logging.info("========DOCS LDA==========")
            logging.info(str(self.docs_lda))
            self.docs = self.docs_lda
        elif(method == 'combined'):
            self.docs_solr = [doc.key for doc in\
                              self.controller.docStore.docsList[0:5]]
            self.docs_kmean = self.controller.run_kmeans()
            self.docs_lda = self.controller.run_lda()
            self.docs = self.controller.run_combine(self.docs_lda,\
                                                    self.docs_kmean,\
                                                    self.docs_solr,\
                                                    self.poids)
        self.submitted_docs.update(self.docs[0:5])
        self.controller.docsSubmittedID = list(self.submitted_docs)
        return self.doc_ids_to_results(self.docs)
    
    
    def run_search_dynamic(self,method):
        if method == "solr":
            self.docs = [doc.key for doc in\
                          self.controller.docStore.docsList[0:5]]
            self.submitted_docs.update(self.docs[0:5])
            self.controller.docsSubmittedID = list(self.submitted_docs)
            return self.doc_ids_to_results(self.docs)
     
        if(method == "lda"):
            controller_lda = Controller(self.new_query,self.domain_name)
            controller_lda.docsSubmittedID = list(self.submitted_docs)
            controller_lda.query = self.query
            self.docs_lda = controller_lda.run_lda()
            self.submitted_docs.update(self.docs_lda)
            self.docs = self.docs_lda
            return self.doc_ids_to_results(self.docs_lda )
        if(method == 'kmeans'):
            self.docs_kmean = self.controller.run_kmeans()
            logging.info("========DOCS KMEAN==========")
            logging.info(str(self.docs_kmean))
            self.docs = self.docs_kmean
            self.submitted_docs.update(self.docs[0:5])
            self.controller.docsSubmittedID = list(self.submitted_docs)
            return self.doc_ids_to_results(self.docs)
        if(method == 'combined'):
            new_query = self.new_query
            self.docs_solr = [doc.key for doc in\
                               self.controller.docStore.docsList[0:5]]
            controller_lda = Controller(new_query,self.domain_name)
            controller_lda.docsSubmittedID = list(self.submitted_docs)
            controller_lda.query = self.query
            self.docs_lda = controller_lda.run_lda()
            self.docs_kmean = self.controller.run_kmeans()
            self.docs = self.controller.run_combine(self.docs_lda,\
                                                    self.docs_kmean,\
                                                    self.docs_solr,\
                                                    self.poids)
            self.submitted_docs.update(self.docs)
            self.controller.docsSubmittedID = list(self.submitted_docs)
            return self.doc_ids_to_results(self.docs)
       
    def doc_ids_to_results(self, doc_ids):
        num_docs = len(doc_ids)
        confidences = [str(int(1000 * random.random()))
                       for _ in xrange(num_docs)]
        results = list(chain(*zip(doc_ids, confidences)))
        logging.info('results returned' + str(results))
        return results
    
    def process_feedback(self, feedbacks):
        # data = json.load(feedbacks)
        file_log = open('example.log','a')
        pprint(feedbacks,file_log)
        file_log.close()
        self.rel_docs = []
        self.non_rel_docs = []
        # time.sleep(10)
        for feedback in feedbacks:
            for subtopic in feedback['subtopics']:
                if self.current_topic in self.feedbacks:
                    self.feedbacks[self.current_topic].\
                    append((\
                            subtopic['subtopic_id'],\
                            feedback['stream_id'],\
                            subtopic['subtopic_name'],\
                            subtopic['passage_text']))
                    self.rel_docs.append(feedback['stream_id'])
                else:
                    self.feedbacks[self.current_topic] = []
                    self.feedbacks[self.current_topic].\
                    append((\
                            subtopic['subtopic_id'],\
                            feedback['stream_id'],\
                            subtopic['subtopic_name'],\
                            subtopic['passage_text']))
                    self.rel_docs.append(feedback['stream_id'])
                    
                logging.info('subtopic_name' +  subtopic['subtopic_name'])
                logging.info('subtopic_id' + str(subtopic['subtopic_id']))
        for doc in self.docs[0:5]:
            if(doc not in self.rel_docs):
                self.non_rel_docs.append(doc)
        feedback_processor = FeedbackPocessing(self.feedbacks,\
                                               self.query_object.raw_query,\
                                               self.controller,\
                                               self.id_topic,\
                                               self.domain_name,\
                                               self.rel_docs,\
                                               self.non_rel_docs)
        self.new_query = feedback_processor.use_feedback(self.feedback_options.pos,\
                                                         self.feedback_options.nb_words_add,\
                                                         self.feedback_options.Ne_list_pos,\
                                                         self.feedback_options.rocchio)
        self.query = self.new_query 
        


def main(options):
    '''Run the recommender system on a sequence of topics.
    '''
    description = ('System using LDA, Kmeans and Solr to optimize diversification and exploitation of different topics')
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--overwrite', action='store_true')
    args = yakonfig.parse_args(parser, [yakonfig])

    logging.basicConfig(level=logging.DEBUG)

    config = yakonfig.get_global_config('harness')
    batch_size = config.get('batch_size', 5)
    run_file_path = config['run_file_path']
    if os.path.exists(run_file_path):
        if args.overwrite:
            os.remove(run_file_path)
        else:
            os.remove(run_file_path)
            # sys.exit('%r already exists' % run_file_path)

    kvl_config = {'storage_type': 'local',
                  'namespace': 'test',
                  'app_name': 'test'}
    kvl = kvlayer.client(kvl_config)
    method,feedback_options,poids,id_config = options[0],options[1],options[2],options[3]
    print method, poids
    system = SearchSystem([],method,feedback_options,poids)
    print args.config
    args.config = 'config' + str(id_config) + '.yaml'
    print args.config
    ambassador = HarnessAmbassadorCLI(system, args.config, batch_size)
    ambassador.run()

def generate_random_weights():
    poids_solr = random.randrange(0,100)
    poids_lda = random.randrange(0, 100-poids_solr)
    poids_kmeans = 100 - poids_solr - poids_lda
    poids_solr = 1.0*poids_solr/100
    poids_lda = 1.0*poids_lda/100
    poids_kmeans = 1.0*poids_kmeans/100
    return (poids_solr,poids_lda,poids_kmeans)

if __name__ == '__main__':
# (0.17, 0.45, 0.38) better ?
    feedback_options = FeedbackOptions(pos = True,nb_words_add = 4,\
                                        NeListPos = True,rocchio = True)
    feedback_options2 = FeedbackOptions(pos = False,nb_words_add = 4,\
                                         NeListPos = False,rocchio = False)
    feedback_options3 = FeedbackOptions(pos = False,nb_words_add = 8,\
                                         NeListPos = False,rocchio = False)
    feedback_options4 = FeedbackOptions(pos = False,nb_words_add = 16,\
                                         NeListPos = False,rocchio = False)

    options_list = [('combined',feedback_options,(0.3, 0.45, 0.25),1),('combined',feedback_options2,(0.3, 0.45, 0.25),2),('combined',feedback_options3,(0.3, 0.45, 0.25),3),('combined',feedback_options4,(0.3, 0.45, 0.25),4)]
    main(options_list[0])
    # pool = Pool(processes=4)
    # data_inputs = options_list
    # pool.map(main, data_inputs)
    # with open("results.txt","a") as result_file:
    #     for option in options_list:
    #         result_cube_test = run_cubeTest(option[3],2)
    #         result_file.write(str(option[0]) + ' ' + option[1].to_string() +\
    #                            ' ' + str(option[2]) + ' score:' +\
    #                             str(result_cube_test) + '\n')
           



