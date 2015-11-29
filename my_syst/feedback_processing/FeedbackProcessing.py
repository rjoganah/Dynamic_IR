'''
Created on 2015-09-02

@author: robinjoganah
'''
import my_syst.preprocessing.parse_xml as pxml
import my_syst.exploitation_exploration.diversification as diversification
from nltk.corpus import stopwords
import nltk
import string


class FeedbackOptions():
    def __init__(self, pos=False, nb_words_add=4, NeListPos=True, rocchio=True):
        self.pos = pos
        self.nb_words_add = nb_words_add
        self.Ne_list_pos = NeListPos
        self.rocchio = rocchio
    def to_string(self):
        list_options = [str(self.pos),str(self.nb_words_add),str(self.Ne_list_pos),str(self.rocchio)]
        return ' '.join(list_options)
        
class FeedbackPocessing(object):
    '''
    classdocs
    '''



    def __init__(self, feedbacks, query, controller, id_topic, domain_name,rel_docs,non_rel_docs):
        self.feedbacks = feedbacks
        self.query = query
        self.controller = controller
        self.new_query = ""
        self.id_topic = id_topic
        self.domain_name = domain_name
        self.rel_docs = rel_docs
        self.non_rel_docs = non_rel_docs
        self.data = controller.data
        self.docs_id = controller.docs_id
        
    def collect_feedback_words(self):
        self.words_to_add = []
        self.NEList = []
        id_topic = self.id_topic
        if id_topic in self.feedbacks:
            for feedback in self.feedbacks[id_topic]:
                if(feedback[1] not in self.rel_docs):
                    self.rel_docs.append(feedback[1])
                words_topic_name = feedback[2]
                passage_text = feedback[3]
                try:
                    tokens = nltk.word_tokenize(' '.join(diversification.NErecognition(passage_text)))
                    tokens_topic_name = nltk.word_tokenize(words_topic_name)
                    self.words_to_add += tokens_topic_name
                    NEList = list(set(tokens))
                    print 'Nelist',NEList
                    print 'Topics title',tokens_topic_name

#                     if(self.domain_name != 'local politics'):
                    if(self.domain_name):
                        NEList = [pxml.stem_and_lemmatize(word) for word in NEList if pxml.lemmatize(word.lower()) not in stopwords.words('english')]
                        tokens_topic_name = [pxml.stem_and_lemmatize(word) for word in tokens_topic_name if pxml.lemmatize(word.lower()) not in stopwords.words('english')]
                except UnicodeError:
                    NEList = []  
                self.NEList += NEList
            return list(set(self.NEList)), list(set(self.words_to_add))
        return [], []
    
    def process_words_feedback(self, words_to_add):
        list_words_to_add = []
        for words in words_to_add:
            list_words_to_add += nltk.word_tokenize(words.lower())
        list_words_to_add = list(set(list_words_to_add))
        if(self.domain_name):
            list_words_to_add = [pxml.stem_and_lemmatize(word) for word in list_words_to_add]
        return list_words_to_add
    
    def add_pos_words(self,words_to_add):
        sentence_to_add = self.clean_words_to_add(words_to_add)
        return sentence_to_add
    
    def add_neg_words(self, words_to_add,weight_neg = 0.5):
        
        sentence_to_add = self.clean_words_to_add(words_to_add)
#         print "cleaned sentence : ", sentence_to_add
        if (len(sentence_to_add) > 0):
            return ' (' + sentence_to_add + ')^-' + str(weight_neg)
        else :
            return sentence_to_add
    
    def clean_words_to_add(self,words_to_add):
        query_tokenized_lower = nltk.word_tokenize(self.query.lower())
        domain_tokenized_lower = nltk.word_tokenize(self.domain_name.lower())
        words_to_add = [word.lower() for word in words_to_add if word.lower() not in domain_tokenized_lower and word.lower() not in query_tokenized_lower and word.lower()]
        sentence_to_add = ' '.join(words_to_add)
        for c in string.punctuation:
                sentence_to_add = sentence_to_add.replace(c, " ")
        return sentence_to_add
    
    def formulate_new_query(self,pos,NeListPos,rocchio,words_to_add,ne_list,words_rocchio):
        sentence_to_add = ' '.join(ne_list) + ' ' + ' '.join(words_to_add)
        for c in string.punctuation:
                sentence_to_add = sentence_to_add.replace(c, " ")

        ne_and_words_title = list(set(nltk.word_tokenize(sentence_to_add.lower())))
#         print 'pos,rocchio,NeListPos : ',pos,rocchio,NeListPos
        if(not pos and len(words_to_add) > 0):
            if(NeListPos and rocchio):
                new_query = self.query  + ' ' + self.add_pos_words(ne_and_words_title) + self.add_neg_words(words_rocchio)
            elif(not NeListPos and rocchio):
                new_query = self.query + ' ' + self.add_neg_words(ne_list + words_to_add) + ' ' + self.add_pos_words(words_rocchio)
                self.query = new_query
            else :
                new_query = self.query + ' ' + self.add_neg_words(ne_list + words_to_add + words_rocchio)
                self.query = new_query
        elif(len(words_to_add) > 0):
            try:
#                 new_query = self.query + ' ' + ' '.join(ne_and_words_title) 
                new_query = self.query + ' ' + self.add_pos_words(list(set(ne_and_words_title)))
                self.query = new_query
            except UnicodeError:
                new_query = self.query + ' ' + ' '.join(words_to_add)
                self.query = new_query        
        if len(words_to_add) == 0 :
#             print "======WORDS ROCCHIO======= : ", words_rocchio
            new_query = self.query + ' ' + self.add_neg_words(words_rocchio)
            
        new_query = self.controller.clean_stopwords(new_query)
                
        return new_query

    def use_feedback(self, pos=False, nb_words_add=4, NeListPos=True, rocchio=True):
#             words_to_add,ne_list = [],[]
        ne_list, words_to_add = self.collect_feedback_words()
        words_to_add = list(set(words_to_add))
        list_words_to_add = self.process_words_feedback(words_to_add)
       
        self.controller.query = self.query
        new_query = self.controller.run_rocchio(self.data, self.docs_id, self.rel_docs, self.non_rel_docs, nbWordsAdd=nb_words_add, posT = True)
        words_rocchio = nltk.word_tokenize(new_query)
        print 'words_rocchio',words_rocchio
        words_to_add = list_words_to_add
#         print "params",':',pos,NeListPos,rocchio,words_to_add,ne_list,words_rocchio
        new_query = self.formulate_new_query(pos,NeListPos,rocchio,words_to_add,ne_list,words_rocchio)
        print "===========new query after rocchio and Clean stopwords=========="
        print new_query
#         print words_rocchio
        
        return new_query
if __name__ == '__main__':
    feedback_options = FeedbackOptions(pos = True,nb_words_add = 4, NeListPos = True,rocchio = True)
    print feedback_options.to_string()
    feedback_processor = FeedbackPocessing('','ebola vaccine','','','','','')
    print feedback_processor.formulate_new_query(pos=True, NeListPos=True, rocchio=True, words_to_add=['ebola', 'vaccine','tumerous'], ne_list=['amazing','news'], words_rocchio=['terrible','news'])
    print feedback_processor.formulate_new_query(pos=True, NeListPos=True, rocchio=True, words_to_add=[], ne_list=[], words_rocchio=['terrible','news'])
    print feedback_processor.formulate_new_query(pos=False, NeListPos=True, rocchio=True, words_to_add=['ebola', 'vaccine','tumerous'], ne_list=['amazing','news'], words_rocchio=['terrible','news'])