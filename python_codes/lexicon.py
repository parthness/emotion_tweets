#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 00:14:40 2017

@author: Parth
"""

datafile="../data/MPQA_lexicon.txt"
lexiconDict={}
posDict={'noun':'n','verb':'v','adj':'a','adverb':'r','anypos':'z'}
polarityDict={'positive':'+','negative':'-','both':'b','neutral':'n'}

with open(datafile,'r') as f:
    for line in f:
        line=line.split()
        word=(line[2].split('=')[1]).strip()
        pos=posDict[(line[3].split('=')[1]).strip()]
        polarity=polarityDict[(line[5].split('=')[1]).strip()]
        if polarity=='+' or polarity=='-':
        	lexiconDict[(word,pos)]=polarity
