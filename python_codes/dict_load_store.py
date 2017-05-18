#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 16:54:32 2017

@author: Parth
"""
from nltk.corpus import wordnet as wn

w=open('../data/emotion_dict_synsets.txt','w')
for emotion,synsets in emoDict.items():
    w.write("-"+emotion+'\n')
    for synset in synsets:
        print(synset.name())
        w.write(synset.name()+'\n')

w.close()
'''
positive=['happy']
negative=['sad','anger','disgust','fear']
emotions=positive+negative+['surprise']

emoDict={}
emotion=''
synsets=[]
with open('../data/emotion_dict_synsets.txt','r') as f:
    for line in f:
        line=line.strip()
        if line[0]=='-':
           if len(synsets)>0:
               emoDict[emotion]=synsets
           synsets=[]
           emotion=line[1:]
        else:
            synsets.append(wn.synset(line))
     
if len(synsets)>0:
    emoDict[emotion]=synsets

emoDict2={}
emotion=''
synsets=[]
with open('../data/synsets_to_add.txt','r') as f:
    for line in f:
        line=line.strip()
        if line[0]=='-':
           if len(synsets)>0:
               emoDict2[emotion]=synsets
           synsets=[]
           emotion=line[1:]
        else:
            synsets.append(wn.synset(line))
     
if len(synsets)>0:
    emoDict2[emotion]=synsets

for emotion in emotions:
    emoDict[emotion]+=emoDict2[emotion]
    emoDict[emotion]=set(emoDict[emotion])
'''