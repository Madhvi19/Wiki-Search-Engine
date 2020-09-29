import nltk
import sys, os, re
import string
import xml.sax
import timeit
from xml.sax.handler import ErrorHandler
import numpy as np
from string import digits
from nltk.tokenize import word_tokenize 
from nltk.corpus import stopwords
from Stemmer import Stemmer
from nltk.stem.snowball import SnowballStemmer
from sortedcontainers import SortedDict
from collections import OrderedDict
from nltk.stem import WordNetLemmatizer
import pickle

def writeToFile(url, index_dict):
    global index_dict
    index_dict=OrderedDict(sorted(index_dict.items(), key=lambda t: t[0]))

    with open(url, 'wb') as handle:
        pickle.dump(dict(index_dict), handle, protocol=pickle.HIGHEST_PROTOCOL)
    
def writeStats(url, total_count, index_dict):
    f = open(index_stat_url, "w")
    f.write(str(total_count)+"\n"+str(len(index_dict.keys())))
    f.close()
