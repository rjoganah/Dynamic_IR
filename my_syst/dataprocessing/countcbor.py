'''
Created on 2015-07-02

@author: robinjoganah
'''
import cbor
import sys
import gzip
import pprint
import json
import csv
import time
import string
import re
from joblib import Parallel, delayed  
import multiprocessing
from multiprocessing import Pool
import index_files
from BeautifulSoup import BeautifulStoneSoup
from BeautifulSoup import BeautifulSoup,NavigableString
import html2text
import nltk
# from pygments.formatters._mapping import content
print sys.stdout.encoding


queue = multiprocessing.Queue()         

def strip_html_nltk(src):

    p=BeautifulSoup(src)

    text=  nltk.clean_html(src)
    text = text.split()
    text = ' '.join(text).encode('UTF-8')
    

    if  p.title:
#         title = p.title.string.replace('\n', ' ')
        title = p.title.string if p.title.string is not None else ' '
    else: title = ' '

    return title.encode("UTF-8"),text
def strip_html(src):
#     print src
#     p = BeautifulStoneSoup(src, convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
    p=BeautifulSoup(src)
    
#     text = p.findAll( text = True )
#     text=  nltk.clean_html(src).encode('utf-8')
#     text_test = text_test.replace('\n', ' ')
#     text_test = text_test.replace('\t', ' ')
#     for c in string.punctuation:
#         text_test= text_test.replace(c,"")
#     print 'result',text_test
    text=p.findAll(text=lambda text:isinstance(text,NavigableString))
    text = " ".join(text)
    text = text.split()
    text = " ".join(text).encode("UTF-8")
    if  p.title:
#         title = p.title.string.replace('\n', ' ')
        title = p.title.string if p.title.string is not None else ' '
    else: title = ' '
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.strip()
    title = title.replace('\n', ' ')
    title = title.replace('\t', ' ')
    title = title.strip()
    for c in string.punctuation:
        text= text.replace(c,"")
        title = title.replace(c, "")
#     
    
    return title.encode("UTF-8"),text
pp = pprint.PrettyPrinter(indent=4)

def count_records_ebola(i,queue = queue):
    infile = '/Users/robinjoganah/Documents/TREC15/dataset/ebola-web-01-2015-' + str(i) + '.cbor.gz'
    startTime = time.time()
    print infile
    if infile.endswith('.gz'):
        fp = gzip.open(infile, 'r')
    else:
        fp = open(infile, 'r')

    count = 0
    try:
        while (1):
            r = cbor.load(fp)
            key = r.get(u'key')
            title,content = strip_html_nltk(r.get('response').get('body'))
            record = (str(key),str(title),str(content))
            queue.put(record)
            count += 1
            end = time.time() 
            if(count == 100):print str(end - startTime)
            
    except EOFError:
        queue.put(STOP_TOKEN)
        end = time.time() 
        print str(end- startTime)
        print count
        
def count_records(i,queue = queue):
    infile = '/Users/robinjoganah/Documents/TREC15/dataset/local-politics-' + str(i) + '.cbor.gz'
    startTime = time.time()
    print infile
    if infile.endswith('.gz'):
        fp = gzip.open(infile, 'r')
    else:
        fp = open(infile, 'r')
    count = 0
    try:
        while (1):
            r = cbor.load(fp)
            key = r.get(u'key')
            title,content = strip_html(r.get('response').get('body'))
            record = (str(key),str(title),str(content))     
            queue.put(record)
            count += 1
            end = time.time() 
            if(count == 100):print str(end - startTime)  
    except EOFError:
        end = time.time() 
        print str(end- startTime)
        print count

def count_records_hacking(i,queue = queue):
#     infile = '/Users/robinjoganah/Documents/TREC15/dataset/bhw.' + str(i) + '.cbor.gz'
    infile = '/Users/robinjoganah/Documents/TREC15/dataset/hackforums-out-fix.' + str(i) + '.cbor.gz'
    startTime = time.time()
    print infile

    if infile.endswith('.gz'):fp = gzip.open(infile, 'r')
    else:fp = open(infile, 'r')

    count = 0
    try:
        while (1):
            r = cbor.load(fp)
            key = r.get(u'key')
            
            features = r.get(u'features')
            if features:                
                items = features.get('items')              
                posts = []
                for item in items:
                    posts.append(item.get('content'))
                    thread_name = item.get('thread_name') if(item.get('thread_name')) else ' '
                posts = ' '.join(posts)
                posts = posts.replace('\n', ' ')
                queue.put((key,thread_name.encode('UTF-8'),posts.encode('UTF-8')))
                         
            count += 1
            end = time.time() 
            if(count == 100):print str(end - startTime)
   
    except EOFError:
        end = time.time() 
        print str(end- startTime)
        print count
        
total = 0
totalRecords = []

def writer_csv(csvFile,queue_write,stop):
#     writerIll = csv.writer(csvfile)
    nb_docs = 0
    tot = 0
    nb_doc_term = 0
    err_list = []
    while True:
        line = queue_write.get()
        if line == stop:
            nb_doc_term +=1
            index_files.commit_files()
            print 'error_list',err_list
            tot += nb_docs
            print tot
            nb_docs = 0
            if(nb_doc_term == 15):
                print 'total docs',tot
                return
            else: 
                line = queue_write.get()
        nb_docs +=1
        val = index_files.indexer_file(line, 'hacking')
        if val != True:
            err_list.append(val)
        
        if(nb_docs == 100):
            tot += nb_docs
            print tot
            index_files.commit_files()
            nb_docs = 0
            



if __name__ == "__main__":
    num_cores = multiprocessing.cpu_count()
    print num_cores
    

    with open('political.csv', 'wb') as csvfile:
        STOP_TOKEN="STOP!!!"
        writer_process = multiprocessing.Process(target = writer_csv, args=(csvfile, queue, STOP_TOKEN))
        writer_process.start()
        pool = Pool(processes=4)
        data_inputs = range(1,16)
        print len(data_inputs)
        print data_inputs
        pool.map(count_records_hacking, data_inputs) 
        writer_process.join()  

