'''
Created on 2015-07-13

@author: robinjoganah
'''
import numpy as np

if __name__ == '__main__':
    f = open('../resultats_comparaison.txt','r+')
    resultats = [float(line[:-1].split()[1]) for line in f]
    print resultats
    count = 0
    methodes = ['results_solr','results_solr_kmean','results_lda_centroides','results_lda','results_kmean']
    resultats_methodes = {'results_solr':[],'results_solr_kmean':[],'results_lda_centroides':[],'results_lda':[],'results_kmean':[]}
    
    while(count < len(resultats) - 3):
        for i,method in enumerate(methodes):
            resultats_methodes[method].append(resultats[i + count])
        count += 5
        
    print 'mean'
    for method in methodes:
        print resultats_methodes[method]
        print np.mean(resultats_methodes[method])
    
    score = {'nulle' : 0}
    for element in zip(resultats_methodes['results_solr'],resultats_methodes['results_solr_kmean'],resultats_methodes['results_lda'],resultats_methodes['results_lda_centroides'],resultats_methodes['results_kmean']):
        index = element.index(max(element))
        if index in score.keys() and max(element) > 0:
            score[index] +=1
        elif index not in score.keys():
            score[index]=1
        elif max(element) == 0:
            score['nulle'] +=1
    print score