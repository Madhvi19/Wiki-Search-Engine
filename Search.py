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
from nltk.stem import WordNetLemmatizer
import pickle

index_url = ""
indexDict = {}
StopWords = set(stopwords.words("english"))
extension = set(["http", "https", "reflist", "yes","curlie","publish","page", "isbn", "file", "jpg", "websit", "cite", "title", "journal","publication", "name", "www","url","link", "ftp", "com", "net", "org", "archives", "pdf", "html", "png", "txt", "redirect", "align", "realign", "valign", "nonalign", "malign", "unalign", "salign", "qalign", "halign", "font", "fontsiz", "fontcolor", "backgroundcolor", "background", "style", "center", "text"])
Stemmer = Stemmer('english')

class Search:
    def print_posting_list(self, field, og_list, list_query, flag):
        
        if flag == True:
            for i in range(len(list_query)):
                if list_query[i] in indexDict:
                    print(og_list[i], ": ",indexDict[list_query[i]])
        else:
            for i in range(len(list_query)):
                if field in indexDict[list_query[i]]:
                    print(og_list[i],": ", indexDict[list_query[i]])
        
                    
    def cleanData(self, data):
        global StopWords, Stemmer
        data = data.lower()
        data = re.sub(r'<(.*?)>','',data)                       # remove html tags
        data = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', data, flags=re.MULTILINE) #Remove Url
        data = re.sub('[^A-Za-z0-9]+',' ',data)

        remove_digits = str.maketrans('', '', digits)
        res = data.translate(remove_digits)
        token_list = word_tokenize(data)
        token_list = [word for word in token_list if word not in StopWords and word not in extension] 
        
        tokens_list = [Stemmer.stemWord(word) for word in token_list]
    
        return token_list, tokens_list

    def processQuery(self, query):
        
        return self.cleanData(query)
        
    def divideAndProcess(self, query):
        title, body, category, references, external_links, infobox = [], [], [], [], [], []
        
        query = query.split()
        
        i = len(query) - 1
        
        while i > 0:
            if ":" not in query[i]:
                query[i-1] +=" "+query[i]
                query[i]=""
            i-=1
        for q in query:
            if len(q) > 2:
                og_list, query_list = self.processQuery(q.split(":")[1])
                self.print_posting_list(str(q.split(":")[0]),og_list, query_list,False)
                

    def isNormalQuery(self, query):
        if ":" in query:
            return False
        return True

def main(query):
    global index_url, indexDict
    
    index_url = sys.argv[1]
    with open(index_url, 'rb') as handle:
        indexDict = pickle.loads(handle.read())
    
    s = Search()
    
    if(s.isNormalQuery(query)):
        og_query, query = s.processQuery(query)
        s.print_posting_list("None", og_query, query, True)

    else:
        s.divideAndProcess(query)
        

if ( __name__ == "__main__"):

    if len(sys.argv)< 3:
        print("Usage : python wikiIndexer.py sample.xml ./output")
        sys.exit(0)
    print("Posting List Formate: word: docID<t Frequency><i Frequency><b Frequency><c Frequency><r Frequency><e Frequency>")
    query = sys.argv[2]
    main(query)


