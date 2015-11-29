import urllib2
import simplejson
from BeautifulSoup import BeautifulStoneSoup
import pickle
docs = []
for qn in range(0,100):
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?q=cuomo&sort=newest&page='+str(qn)+'&api-key=8caee469a03cae0c8425dc405565dd21:15:72079770'
    
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    
    # Process the JSON string.
    results = simplejson.load(response)
    articles = [ BeautifulStoneSoup(doc['lead_paragraph'], convertEntities=BeautifulStoneSoup.HTML_ENTITIES) if doc['lead_paragraph'] else ' '   for doc in results['response']['docs'] ]
    docs += articles

for qn in range(101,200):
    print qn
    url = 'http://api.nytimes.com/svc/search/v2/articlesearch.json?q=cuomo&sort=newest&page='+str(qn)+'&api-key=8caee469a03cae0c8425dc405565dd21:15:72079770'
    
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    
    # Process the JSON string.
    results = simplejson.load(response)
    articles = [ BeautifulStoneSoup(doc['lead_paragraph'], convertEntities=BeautifulStoneSoup.HTML_ENTITIES) if doc['lead_paragraph'] else ' '   for doc in results['response']['docs'] ]
    docs += articles
for index,doc in enumerate(docs):
    print 'article :' + str(index)
    print doc
print len(docs)
pickle.dump(docs, open( "articlesCuomo.p", "wb" ) )


# now have some fun with the results...