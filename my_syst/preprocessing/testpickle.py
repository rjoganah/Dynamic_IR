'''
Created on 2015-05-14

@author: robinjoganah
'''
import csv
import pickle

if __name__ == '__main__':
    docs = pickle.load( open( "articles2.p", "rb" ) )
    # with open('articlesNY.csv', 'wb') as csvfile:
    #     articlesWriter = csv.writer(csvfile)
    #     for doc in docs:
    #         print doc
    #         articlesWriter.writerow(doc[:])
    
        
    f = open('articlesNY.txt', 'r+')
    f.truncate()
    for index,doc in enumerate(docs):
        f.write(str(index) +' ' + str(doc))
        f.write('\n')
        
    
    import cbor
    import sys
    import gzip
    
    def count_records(infile):
        if infile.endswith('.gz'):
            fp = gzip.open(infile, 'r')
        else:
            fp = open(infile, 'r')
    
        count = 0
        try:
            while (1):
                cbor.load(fp)
                count += 1
        except EOFError:
            return count
    
    total = 0
    
    for infile in sys.argv[1:]:
        count = count_records(infile)
        print infile, count
        total += count
        
    if total != count:
        print "total", total