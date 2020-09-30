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
from nltk.stem import WordNetLemmatizer
import pickle
import timeit
import math
from collections import OrderedDict
import bisect

secondaryIndex = {}                                                #Stores First Word of Every Primary Index and It's Path  
titleIDMapping = {}                                                #Stores Document ID Against It's Title and Total Number of Words Present in the Doc 
start = 0
startGlobal = 0
que = 0
path = "/home/madhvi/IRE/Mini_Project/Index/"
StopWords = set(stopwords.words("english"))
extension = set(["http", "https", "reflist", "yes","curlie","publish","page", "isbn", "file", "jpg", "websit", "cite", "title", "journal","publication", "name", "www","url","link", "ftp", "com", "net", "org", "archives", "pdf", "html", "png", "txt", "redirect", "align", "realign", "valign", "nonalign", "malign", "unalign", "salign", "qalign", "halign", "font", "fontsiz", "fontcolor", "backgroundcolor", "background", "style", "center", "text"])
Stemmer = Stemmer('english')

def loadSecondaryIndex():
    global path, secondaryIndex
    with open(path+"SecondaryIndex", 'rb') as handle:
        secondaryIndex = pickle.loads(handle.read())

def loadMappingDict():
    global path, titleIDMapping
    with open(path+"docIDTitleMapping", 'rb') as handle:
        titleIDMapping = pickle.loads(handle.read())

def isNormalQuery(query):
    if ":" in query:
            return False
    return True

def processQuery(listQuery):
    frequencyDocMap = {}
    for query in listQuery:
        field = query.split(":")[0]
        wordList = cleanQuery(query.split(":")[1])
        primaryIndexLinks = findPILinks(wordList)
        postingLists = findPostingLists(primaryIndexLinks)
        freqMap = convertToTFIDF(postingLists, field)
        for docID, score in freqMap.items():
            if docID in frequencyDocMap.items():
                frequencyDocMap[docID] += score
            else:
                frequencyDocMap[docID] = score
    return frequencyDocMap


def divideAndProcessQuery(query):
    query = query.split()
    i = len(query) - 1

    while i > 0:
        if ":" not in query[i]:
            query[i-1] +=" "+query[i]
            query[i]=""
        i-=1
    sorted_query = []
    for q in query:
        if(q!=""):
            sorted_query.append(q)
    return processQuery(sorted_query)


def BinSearch(keys, word):
    global secondaryIndex
    
    i = bisect.bisect_left(keys, word)

    if i < len(keys):
        if (keys[i] == word):
            return secondaryIndex[keys[i]]
        else:
            return secondaryIndex[keys[i-1]]
    else:
          return secondaryIndex[keys[i-1]]


def findPILinks(wordList):
    global secondaryIndex
    piDict={}
    keys = list(secondaryIndex.keys())
    for word in wordList:
        url = BinSearch(keys, word)
        if url in piDict:
            piDict[url].append(word)
        else:
            piDict[url] = [word]
    return piDict


def findPostingLists(primaryIndexLinks):
    postingLists={}
    for url, words in primaryIndexLinks.items():
        pIndex ={}
        with open(url, 'rb') as handle:
            pIndex = pickle.loads(handle.read())
        for word in words:
            if word in pIndex:
                postingLists[word]=pIndex[word]
    return postingLists


def calculateIDF(postingLists, field):
    global titleIDMapping
    total_docs = len(titleIDMapping)
    docs_contain_word = len(postingLists)

    return total_docs/(1+docs_contain_word)

def calculateTotalCount(poList):
    total, t, b, c, ib, r, e = 0,0,0,0,0,0,0
    
    if 'b' in poList:
        po = poList.split('b')[1]
        i = 0
        while i<len(po) :
            if po[i].isdigit() == True:
                b = b*10+ int(po[i])
            else:
                break
            i += 1
    
    if 'c' in poList:
        po = poList.split('c')[1]
        i = 0
        while i<len(po) :
            if po[i].isdigit() == True:
                c = c*10 + int(po[i])
            else:
                break
            i += 1
        
    if 'i' in poList:
        po = poList.split('i')[1]
        i = 0
        while i<len(po) :
            if po[i].isdigit() == True:
                ib = ib*10 +int(po[i])
            else:
                break
            i += 1
            
    if 't' in poList:
        po = poList.split('t')[1]
        i = 0
        while i<len(po) :
            if po[i].isdigit() == True:
                t = t*10 + int(po[i])
            else:
                break
            i += 1
    
    if 'r' in poList:
        po = poList.split('r')[1]
        i = 0
        while i<len(po) :
            if po[i].isdigit() == True:
                r = r*10 + int(po[i])
            else:
                break
            i += 1
            
    if 'e' in poList:
        po = poList.split('e')[1]
        i = 0
        while i<len(po) :
            if po[i].isdigit() == True:
                e = e*10+ int(po[i])
            else:
                break
            i += 1
        
    total =int(t)*0.35+int(b)*0.25+int(ib)*0.20+int(c)*0.10+int(r)*0.7+int(e)*0.3
    
    return total


def calculateTotalCountFQ(poList, weight, field):
    weightPointer, total, t, b, c, ib, r, e, f = 0,0,0,0,0,0,0,0,0
    
    Fields= ['t', 'b', 'i', 'c', 'r', 'l']
    weigthPointer=Fields.index(field)
    
    if field in poList:
        po = poList.split(field)[1]
        i = 0
        while i<len(po) :
            if po[i].isdigit() == True:
                f = f*10+ int(po[i])
            else:
                break
            i += 1
        f = f * weight[weightPointer]
           
    else:
        weightPointer=len(weight)-1
        if "t" in poList and "t" != field:
            po = poList.split("t")[1]
            i = 0
            while i<len(po) :
                if po[i].isdigit() == True:
                    t = t*10+ int(po[i])
                else:
                    break
                i += 1
            t = t * weight[weightPointer]

        elif "b" in poList and "b" != field:
            po = poList.split("b")[1]
            i = 0
            while i<len(po) :
                if po[i].isdigit() == True:
                    b = b*10+ int(po[i])
                else:
                    break
                i += 1
            b = b * weight[weightPointer]
            weightPointer+=1
    
        elif "i" in poList and "i" != field:
            po = poList.split("i")[1]
            i = 0
            while i<len(po) :
                if po[i].isdigit() == True:
                    ib = ib*10+ int(po[i])
                else:
                    break
                i += 1
            ib = ib * weight[weightPointer]
            weightPointer+=1

        elif "c" in poList and "c" != field:
            po = poList.split("c")[1]
            i = 0
            while i<len(po) :
                if po[i].isdigit() == True:
                    c = c*10+ int(po[i])
                else:
                    break
                i += 1
            c = c * weight[weightPointer]
            weightPointer+=1

        elif "r" in poList and "r" != field:
            po = poList.split("r")[1]
            i = 0
            while i<len(po) :
                if po[i].isdigit() == True:
                    r = r*10+ int(po[i])
                else:
                    break
                i += 1
            r = r * weight[weightPointer]
            weightPointer+=1


        elif "e" in poList and "e" != field:
            po = poList.split("e")[1]
            i = 0
            while i<len(po) :
                if po[i].isdigit() == True:
                    e = e*10+ int(po[i])
                else:
                    break
                i += 1

            e = e * weight[weightPointer]
            weightPointer+=1

    total = f + t + b + ib + c + r + e
    return total


def calculateTF(poList,field):
    global titleIDMapping
    docid = int(poList.split(":")[0])
    total_words_in_doc = titleIDMapping[docid][1]
    if field == 'x':
        count_word_in_doc = calculateTotalCount(poList)
        tf = count_word_in_doc/total_words_in_doc
        
        return tf
    
    weights = [0.25, 0.25, 0.15, 0.12, 0.12, 0.12,0.07]
    
    count_word_in_doc = calculateTotalCountFQ(poList, weights, field)
    
    tf = count_word_in_doc/total_words_in_doc
    return tf
    

def convertToTFIDF(postingLists, field):
    freqDocMapping = {}
    for word, postingList in postingLists.items():
        postingList = postingList.split("|")
        idf = calculateIDF(postingList, field)
        for po in postingList:
            tf = calculateTF(po,field)
            score = tf*math.log(idf,10)
            docID  = po.split(":")[0]
            if docID in freqDocMapping:
                freqDocMapping[docID] += score
            else:
                freqDocMapping[docID] = score
                
    return freqDocMapping


def printResult(k, d):
    global titleIDMapping, start,startGlobal, que
    d=OrderedDict(sorted(d.items(), key=lambda t: t[1], reverse=True))
    f= open("./queries_op.txt", "a")
    for key, value in d.items():
        if(k>0):
            f.write(str(key)+","+titleIDMapping[int(key)][0]+"\n")
        k-=1
    stop = timeit.default_timer()
    f.write(str(stop - start)+" sec"+", "+str((stop-startGlobal)/que)+"\n"+"\n")
    f.close()


def cleanQuery(data):
    global StopWords, Stemmer, extension
    data = data.lower()
    data = re.sub(r'<(.*?)>','',data)                                                                                              # Remove HTML Tags
    data = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', data, flags=re.MULTILINE) # Remove Url
    data = re.sub('[^A-Za-z0-9]+',' ',data)                                                                                        # Remove Special characters
    token_list = word_tokenize(data)                                                                                               # Tokenize String
    token_list = [word for word in token_list if word not in StopWords and word not in extension]                                  # Remove StopWords and Extended StopWords
    tokens_list = [Stemmer.stemWord(word) for word in token_list]
    return tokens_list


def main(k, query):    
    if(isNormalQuery(query)):
        wordList = cleanQuery(query)
        primaryIndexLinks = findPILinks(wordList)
        postingLists = findPostingLists(primaryIndexLinks)
        freqDocMapping = convertToTFIDF(postingLists, 'x')
        printResult(k, freqDocMapping)
    else:
        freqDocMapping=divideAndProcessQuery(query)
        printResult(k,freqDocMapping)


if (__name__ == "__main__"):
    loadSecondaryIndex()
    loadMappingDict()
    
    fileName = "./queries.txt"
    queries= open(fileName).readlines()

    startGlobal = timeit.default_timer()
    for query in queries:
        que+=1
        start = timeit.default_timer()
        query= query.strip('\n')
        k = int(query.split(",")[0])
        query= query.split(',')[1]
        main(k, query)