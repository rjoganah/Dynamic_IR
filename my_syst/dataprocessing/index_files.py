'''
Created on 2015-07-31

@author: robinjoganah
'''

import pysolr
import solr
import logging
import pickle
from my_syst.nlp_utils.idf import transform_tf_idf
# -*- coding: utf-8 -*-
logging.basicConfig(filename='example.log',level=logging.DEBUG)
conn = solr.SolrConnection('http://localhost:8983/solr')
solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)


topicList = []    
topicComplete = []
topicNotComplete = []
def indexer_file(doc,topic):
    try:
        conn.add(id = doc[0].encode("UTF-8"), title = doc[1].decode("UTF-8"), content = doc[2].decode("UTF-8"), subject = topic)
        return True
    except:
        return doc[0]
        
def commit_files():
    conn.commit()  


def delete_all_docs():
    solr.delete(q='*:*')
    
def requete(q,nbrows = 25):
#     'title:' + q + ' content:' +
    response = conn.query( q + ' fl=*,score',rows = nbrows)
    return [(hit['title'][0] + ' ' + hit['content'][0],hit['score'],[]) for hit in response.results],[hit['id'] for hit in response.results]
   
if __name__ == "__main__":
    data,docs_id = requete(q = 'subject:(local politics)',nbrows = 30000)
    print len(data)
    text = [dat[0] for dat in data]
    tf_idf_vect = transform_tf_idf(text,'local_politics')
    pickle.dump(tf_idf_vect, open( "tf_idf_" + 'local_politics2' + ".p", "wb" ) )
        
#     time_start = time.time()
# #     for i,element in enumerate(requete(q = 'subject:(local politics) AND content:(squamish canada land disput  ( cbc news crash gt )^-1) ')):
# #         print i,element
#     data,docs_id = requete(q = 'subject:(local politics) AND content:(obama Bedfellow^-0.2 ( cbc news crash gt  ) ^-10) ')
#     for i,doc in enumerate(data):
#         
#         if(i>10):
#             print i,doc
#             
#     print 'request time : ' + str(time.time() - time_start)

