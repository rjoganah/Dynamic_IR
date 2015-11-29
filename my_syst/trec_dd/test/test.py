'''
Created on 2015-05-05

@author: robinjoganah
'''
import unittest
import numpy as np
from ExpectationMaximization import ExpectationMaximization
from query_expansion.Rocchio import SearchAlgorithms

class Test(unittest.TestCase):


    def test_proba_d_s_c(self):
        d = np.array([0,1,1,0,1])
        c = [0] * 3
        c[2] = np.array([.2,.5,.3,.8,0.2])
        c[1] = np.array([.2,.5,.3,.8,0.2])
        c[0] = np.array([.1,.3,.4,.5,1.2])
        expectation_maximization = ExpectationMaximization()
        results = expectation_maximization.proba_d_s_c(d,c)
        assert(np.array_equal(results,np.array([0.27197619539226908, 0.36401190230386543, 0.36401190230386543]))),"Erreur avec la fonction test_proba d sachant c" 
        
    def test_rocchio_algorithm(self):
        roc = SearchAlgorithms()
        query = np.array([[1,0,0,1,0,0]])
        relev_documents = np.array([[0,1,0,1,0,0],[0,1,1,1,0,0]])
        non_relev_documents = np.array([[1,0,0,0,0,1],[1,1,0,0,0,1]])
        assert((np.array([[ 0.75,0.75,0.,1.75,0.,-0.25 ]]) == roc.rocchio_algorithm(query,relev_documents,non_relev_documents)).all())
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()