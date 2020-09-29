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
from Indexer import *

docID = 0
total_count = 0
clean_count = 0
TitleIDMap = {}
StopWords = set(stopwords.words("english"))
extension = set(["http", "https", "reflist", "yes","curlie","publish","page", "isbn", "file", "jpg", "websit", "cite", "title", "journal","publication", "name", "www","url","link", "ftp", "com", "net", "org", "archives", "pdf", "html", "png", "txt", "redirect", "align", "realign", "valign", "nonalign", "malign", "unalign", "salign", "qalign", "halign", "font", "fontsiz", "fontcolor", "backgroundcolor", "background", "style", "center", "text"])
Stemmer = Stemmer('english')
index_dict = {}
small_dict = {}

def cleanData(data):
    global StopWords, Stemmer, total_count
    data = re.sub(r'<(.*?)>','',data)                                                                          # Remove HTML Tags
    data = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', data, flags=re.MULTILINE)  #Remove Url
    data = re.sub('[^A-Za-z0-9]+',' ',data)                                                                    # Remove Punctuation and Special Characters
    token_list = word_tokenize(data)                                                                           # Tokenize String
    total_count += len(token_list)
    token_list = [word for word in token_list if word not in StopWords and word not in extension]              #Remove Stopwords and Extended Stopwords
    token_list = [Stemmer.stemWord(word) for word in token_list]                                               #Stem words 
    
    return token_list


def create_small_dict(data, field):
    global small_dict
    for word in data:
        if len(word)>2 and len(word)<9:
            if word in small_dict:
                small_dict[word][field]+=1
            else:
                small_dict[word] = [0,0,0,0,0,0]
                small_dict[word][field] = 1



def create_dict():
    global small_dict, docID, index_dict
    
    for word, postingList in small_dict.items():
        if word in index_dict:     
            index_dict[word] += '|'+ str(docID)
            if postingList[0] != 0:
                index_dict[word] += 't'+ str(postingList[0])
            if postingList[1] != 0:
                index_dict[word] += 'i'+ str(postingList[1])
            if postingList[2] != 0:
                index_dict[word] += 'b'+ str(postingList[2])
            if postingList[3] != 0:
                index_dict[word] += 'c'+ str(postingList[3])
            if postingList[4] != 0:
                index_dict[word] += 'r'+ str(postingList[4])
            if postingList[5] != 0:
                index_dict[word] += 'e'+ str(postingList[5])
            
        else:
            index_dict[word ]= str(docID)
            if postingList[0] != 0:
                index_dict[word] += 't'+ str(postingList[0])
            if postingList[1] != 0:
                index_dict[word] += 'i'+ str(postingList[1])
            if postingList[2] != 0:
                index_dict[word] += 'b'+ str(postingList[2])
            if postingList[3] != 0:
                index_dict[word] += 'c'+ str(postingList[3])
            if postingList[4] != 0:
                index_dict[word] += 'r'+ str(postingList[4])
            if postingList[5] != 0:
                index_dict[word] += 'e'+ str(postingList[5])


def findExternalLinks(data):
    links = []
    lines =data.split("== external links ==")
    if len(lines)>1:
        lines = lines[1].split('\n')      
        for i in range(len(lines)):
            if "* [" in lines[i] or "*[" in lines[i]:
                  links.extend(lines[i].split('[')[1].split("]")[0].split())
    
     
    lines =data.split("==external links==")
    if len(lines)>1:
        lines = lines[1].split('\n')      
        for i in range(len(lines)):
            if "* [" in lines[i] or "*[" in lines[i]:
                  links.extend(lines[i].split('[')[1].split("]")[0].split())
    
    return links


def processText(data):
    global docID
    data = data.lower()
    lines = data.split('\n')
    
    infobox, category, body, references, external_links = [], [], [], [], []
    
    external_links = findExternalLinks(data)
    body_flag=True
    
    for i in range(len(lines)):
        if '{{infobox' in lines[i]:
            bracket_count = 0
            infobox.extend(lines[i].split('{{infobox')[1:])
            while(True):
                if '{{' in lines[i]:
                    bracket_count += lines[i].count('{{')
                if '}}' in lines[i]:
                    bracket_count -= lines[i].count('}}')
                if bracket_count <= 0:
                    break
                i += 1
                try:
                    infobox.extend(lines[i].split())
                except:
                    break
        
        elif "[[category" in lines[i]:
            body_flag = False
            try:
                category.extend(lines[i].split(":")[1].split("]]")[0].split())
            except:
                category.extend(lines[i].split())    

        elif "==references==" in lines[i] or "== references ==" in lines[i]:
            body_flag =False
            i+=1
            while i<len(lines):
                if "[[category" or "=="in lines[i]:
                    break
                elif "{{cite" in lines[i] or "{{vcite" in lines[i]:
                    line= lines[i].split("title=")
                    if(len(line)>1):
                        references.append(line[1].split('|')[0])
                elif '{{' in lines[i] and 'ref' not in lines[i]:
                    references.append(line[1].split('{{')[1].split('}}'[0]))
                i+=1
        
        elif body_flag == True:
            body.extend(lines[i].split())

            
    infobox = cleanData(" ".join(infobox))
    body = cleanData(" ".join(body))
    category = cleanData(" ".join(category))
    references = cleanData(" ".join(references))
    external_links = cleanData(" ".join(external_links))
    
    create_small_dict(TitleIDMap[docID], 0)
    create_small_dict(infobox, 1)
    create_small_dict(body, 2)
    create_small_dict(category, 3)
    create_small_dict(references, 4)
    create_small_dict(external_links, 5)
    
    create_dict()
    small_dict.clear()

class DataHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.currentTag = ""
        self.title = ""
        self.text = ""
        
    def startElement(self,tag, attributes):
        global docID
        if tag == "page":
            docID += 1
        self.currentTag = tag
        
    def characters(self, content):
        if self.currentTag == "title":
            self.title += content
        elif self.currentTag == "text":
            self.text += content
            
    def endElement(self, tag):
        global docID
        if self.currentTag == "title":
            TitleIDMap[docID] = cleanData(self.title.lower())
            self.title = ""
         
        elif self.currentTag == "text":
            processText(self.text)
            self.text=""
        self.currentTag=""


def main():
    global index_dict, total_count
    dump_url = sys.argv[1]
    index_url = sys.argv[2]
    index_stat_url = sys.argv[3]
    parser = xml.sax.make_parser()                                   # create XML parser
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)         # switch off for namespace
    handler = DataHandler()                                          # content handler child class with overriden methods
    parser.setContentHandler(handler)                                # set overriden class
    parser.parse(dump_url)                                           # parse data
 
    writeToFile(index_url, index_dict)                               # writes index into secondary memory
    writeStats(index_stat_url, total_count, index_dict)              # writes stats of the Index
    
    index_dict.clear()


if ( __name__ == "__main__"):
    
	start = timeit.default_timer()

	if len(sys.argv)!= 4:
		print("Usage : python wikiIndexer.py sample.xml ./output")
		sys.exit(0)

	main()  
	stop = timeit.default_timer()
	print(stop - start, "sec")
