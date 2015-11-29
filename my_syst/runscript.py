'''
Created on 2015-07-13

@author: robinjoganah
'''
import subprocess

def run():
    pipe = subprocess.Popen(["perl","run.pl"], stdout=subprocess.PIPE)