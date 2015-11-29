import xml.etree.ElementTree as ET
from nltk.stem import WordNetLemmatizer
import nltk
import os
import re
from nltk.stem import PorterStemmer
path = os.path.dirname(os.path.abspath(__file__))
# from nltk.corpus import wordnet as wn
# import enchant

# def is_known(word):
#     """return True if this word "exists" in WordNet
#        (or at least in nltk.corpus.stopwords)."""
#     d = enchant.Dict("en_US")
#     if d.check(word):
#     	return True
#     # if word.lower() in nltk.corpus.stopwords.words('english'):
#     #     return True
#     synset = wn.synsets(word)
#     print synset
#     if len(synset) == 0:
#         return False
#     else:
#         return True
# import enchant
def create_dict_query_domain():
	#Create dictionnary with each query and the corresponding domain name (Ebola,Hacking or Local Politics)
	tree = ET.parse('truth_data.xml')
	root = tree.getroot()
	query_domain = {}
	for child in root:
		for subchild in child:
			query_domain[subchild.attrib['name']] = child.attrib['name']
	return query_domain

def load_list_words_english_frequent():
	f = open(path + '/list_words.txt', 'r')
	list_words = []
	for line in f:
		line = re.sub(r'[^\w]', ' ', line)
		list_words.append(nltk.word_tokenize(line)[0])
	return list_words


def lemmatize(word):

	lemmatizer = WordNetLemmatizer()

	return lemmatizer.lemmatize(word)

def stem_and_lemmatize(word):
	stemmer = PorterStemmer()
	lemmatizer = WordNetLemmatizer()
	return stemmer.stem(lemmatizer.lemmatize(word))

if __name__ == '__main__':
	# print create_dict_query_domain()
	for word in nltk.word_tokenize('ebola, proxies proxy manchester www oktm http png ? but it\'s time to accept that : time is time'):
		stemmer = PorterStemmer()
		# print is_known(word)
		print stemmer.stem(lemmatize(word))
	# print html.entities.html5
	print load_list_words_english_frequent()