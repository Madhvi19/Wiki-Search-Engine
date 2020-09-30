import sys, os, re
import string
import timeit
from sortedcontainers import SortedDict
from collections import OrderedDict
import pickle
import heapq

secondary_dict = {}

def writeToFile(url, index_dict):
    index_dict=OrderedDict(sorted(index_dict.items(), key=lambda t: t[0]))
    with open(url, 'wb') as handle:
        pickle.dump(dict(index_dict), handle, protocol=pickle.HIGHEST_PROTOCOL)
    
def writeStats(url, total_count, index_dict):
    f = open(url, "w")
    f.write(str(total_count)+"\n"+str(len(index_dict.keys())))
    f.close()

def writeFinalIndex(data, countFinalFile, index_url):
    global secondary_dict
    iterator = iter(data)
    secondary_dict[next(iterator)] = index_url+"FinalIndex"+str(countFinalFile)
    
    print("FINAL INDEX SIZE: ", len(data))
    with open(index_url+'FinalIndex'+str(countFinalFile), 'wb') as handle:
        pickle.dump(dict(data), handle, protocol=pickle.HIGHEST_PROTOCOL)

    return countFinalFile+1

def writeSecondaryIndex(url):
    global secondary_dict
    with open(url+'SecondaryIndex', 'wb') as handle:
        pickle.dump(dict(secondary_dict), handle, protocol=pickle.HIGHEST_PROTOCOL)

def merge_files(index_url, total_files):
    listOfWords, indexFile, topOfFile = {}, {}, {}
    flag = [0]*total_files
    data = {}
    heap = []
    countFinalFile=0
    for i in range(total_files):
        fileName = index_url+'index'+str(i) 
        indexFile[i] = open(fileName, 'r')
        flag[i] = 1
        topOfFile[i] = indexFile[i].readline().strip()
        listOfWords[i] = topOfFile[i].split("-")
        if listOfWords[i][0] not in heap:
            heapq.heappush(heap, listOfWords[i][0])

    count=0
    while any(flag)==1:
        temp = heapq.heappop(heap)
        count += 1
        for i in range(total_files):
            if flag[i]:
                if listOfWords[i][0] == temp:
                    if temp in data:
                        data[temp]+="|"+listOfWords[i][1]
                    else:
                        data[temp]=listOfWords[i][1]
                        
                    topOfFile[i] = indexFile[i].readline().strip()
                    if topOfFile[i] == '':
                            flag[i] = 0
                            indexFile[i].close()
                            os.remove(index_url+'index'+str(i))
                    else:
                        listOfWords[i] = topOfFile[i].split("-")
                        if listOfWords[i][0] not in heap:
                            heapq.heappush(heap, listOfWords[i][0])

        if count > 0 and count%30000==0:
            countFinalFile=writeFinalIndex(data, countFinalFile, index_url)
            data={}
    countFinalFile = writeFinalIndex(data, countFinalFile, index_url)

def writeTitleDocIDMapping(url, TitleIDMap):
    with open(url+'docIDTitleMapping', 'wb') as handle:
        pickle.dump(dict(TitleIDMap), handle, protocol=pickle.HIGHEST_PROTOCOL)

