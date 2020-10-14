![Python 3](https://img.shields.io/badge/Python-3-green)

# Wiki-Search-Engine:
An efficient and scalable Search Engine built using Python on English Wikipedia dump, which is capable of creating an optimized Inverted index using K-Way Merge Sort and provides support for Field as well as Normal query search using TF-IDF Ranking.
Problem Statement:
A search engine is to be built on the Wikipedia Data Dump of size ~50 GB without using any external index. The search results should be returned in real-time. 
Support for multi-word and multi-field query search is to be implemented.
Need to rank the documents and display only the top K most relevant documents.
Search should take <5 seconds and the index should be ~25% of the dump size.

# Specifications:

Parsing: Read through the raw dump & extract essential words/phrases for indexing & searching
Partial Indexes: Extracting & storing essential information in small partial indexes
The Global Index: Merging the partial indexes to obtain a sorted big index.
Search: Performing multi-word / multi-field queries

# Code Walkthrough:

The repository contains the following files:

Parser.py: This file creates the entire index in a field separated manner. Along with the index files, it also creates the offsets for the same as a Secondary index. It also creates a map for the title and the document id along with its offset. 

Search.py - This function takes as input the query and returns the top K results from the Wikipedia corpus. 
Steps to Run the Code:

# How To Run the Code:

To execute parsing on the entire data dump, run the following command: python3 parser.py path_to_wikipedia_dump path_to_Index_folder

To execute search.py, list queries in a file named “queries.txt” run the following command: python3 search.py path_to _query.txt
