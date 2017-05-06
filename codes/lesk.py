#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2017 alvations
# URL:
# For license information, see LICENSE.md
import math
from itertools import chain
import string
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from senti_classifier.senti_classifier import synsets_scores
from pywsd.utils import lemmatize, porter, synset_properties
from positive_negative_lexicon import lexiconDict
from wordSenseDisambiguate import disgustingWords

EN_STOPWORDS = stopwords.words('english')+list(string.punctuation)

def findRelatedForms(ss):
    drfList=[]
    lemmas=ss.lemmas()
    for lemma in lemmas:
        drfs=lemma.derivationally_related_forms()
        for drf in drfs:
            drfList.append(drf.synset().name().split('.')[0])

    return list(set(drfList))

def simple_signature(word,ss,lexicon):
    """
    Returns a synsets_signatures dictionary that includes signature words of a
    sense from its:
    (i)   definition
    (ii)  example sentences
    (iii) hypernyms and hyponyms
    """
    signature=[wn.morphy(word),word,ss.name().split('.')[0]]+findRelatedForms(ss)
    print('signature',signature)
   # print("ss: ",ss)
    # Includes definition.
    ss_definition = synset_properties(ss, 'definition')
    signature+=word_tokenize(ss_definition)
    # Includes examples
    #ss_examples = synset_properties(ss, 'examples')
    #signature+=list(chain(*[i.split() for i in ss_examples]))
    # Includes lemma_names.
    ss_lemma_names = synset_properties(ss, 'lemma_names')
    signature+= ss_lemma_names
    # Optional: includes lemma_names of hypernyms and hyponyms.
    
    ss_hyponyms = synset_properties(ss, 'hyponyms')
    #ss_hypernyms = synset_properties(ss, 'hypernyms')
    ss_hypohypernyms = ss_hyponyms#+ss_hypernyms
    signature += list(chain(*[i.lemma_names() for i in ss_hypohypernyms]))
  #  print(signature)
    
    # Includes holonyms.
    ss_mem_holonyms = synset_properties(ss, 'member_holonyms')
    ss_part_holonyms = synset_properties(ss, 'part_holonyms')
    ss_sub_holonyms = synset_properties(ss, 'substance_holonyms')
    # Includes meronyms.
    ss_mem_meronyms = synset_properties(ss, 'member_meronyms')
    ss_part_meronyms = synset_properties(ss, 'part_meronyms')
    ss_sub_meronyms = synset_properties(ss, 'substance_meronyms')
    # Includes similar_tos
    #ss_simto = synset_properties(ss, 'similar_tos')
    
    related_senses = list(set(ss_mem_holonyms+ss_part_holonyms+
                              ss_sub_holonyms+ss_mem_meronyms+
                              ss_part_meronyms+ss_sub_meronyms))

    signature += list([j for j in chain(*[synset_properties(i, 'lemma_names')
                                         for i in related_senses])
                      if j not in EN_STOPWORDS])
  #  print(signature)
    # Optional: removes stopwords.
    signature = [i for i in signature if type(i)==str]
    signature = [i for i in signature if i.lower() not in EN_STOPWORDS]
    # Lemmatized context is preferred over stemmed context.
    signature = [lemmatize(i) for i in signature]
    # Matching exact words may cause sparsity, so optional matching for stems.
    #signature = [porter.stem(i) for i in signature]
    
    ss_sign=set(signature)
    to_remove=[]

    for word in ss_sign:
        morphy=wn.morphy(word)
        if lexicon=='+-':
            if (word,'z') not in lexiconDict and (morphy,'z') not in lexiconDict:
                to_remove.append(word)
        else:
            if (word,'z') in lexiconDict:
                if lexiconDict[(word,'z')]!=lexicon:
                    to_remove.append(word)
            elif (morphy is not None) and (morphy,'z') in lexiconDict:
                if lexiconDict[(morphy,'z')]!=lexicon:
                    to_remove.append(word)
            else:
                to_remove.append(word)
    
    to_remove=set(to_remove)
    ss_sign=ss_sign-to_remove
    signature=list(ss_sign)
    
    sim=[]
    for ss in ss_sign:
        synsets=wn.synsets(ss)
        if len(synsets)>0:
            if synsets[0] not in sim:
                synset=synsets[0]   
                '''
                pos=synsets_scores[synset.name()]['pos']
                neg=synsets_scores[synset.name()]['neg']
                if(pos>0.125 or neg>0.125):     
                    sim.append(synset)
                else:
                    signature.remove(ss)
                '''
                pos=synset.pos()
                morphy=wn.morphy(ss,pos)
                if (ss,pos) in lexiconDict or (ss,'z') in lexiconDict or ss in disgustingWords:
                    sim.append(synset)
                elif (morphy is not None) and ((morphy,'z') in lexiconDict or (morphy,pos) in lexiconDict):
                    sim.append(synset)
                else:
                    signature.remove(ss)
        else:
            signature.remove(ss)
    return [signature,sim]
    '''
    sim=[]
    for ss in ss_sign:
        synsets=wn.synsets(ss)
        if len(synsets)>0:
            if synsets[0] not in sim:
                synset=synsets[0]   
                pos=synsets_scores[synset.name()]['pos']
                neg=synsets_scores[synset.name()]['neg']
                if(pos>neg or neg>pos):     
                    sim.append(synset)
    
    return set(signature+sim)
    '''

def similarity_lesk(ss_sign1, ss_sign2):
    """
    This function is the implementation of the Adapted Lesk algorithm,
    described in Banerjee and Pederson (2002). It makes use of the lexical
    items from semantically related senses within the wordnet
    hierarchies and to generate more lexical items for each sense.
    see www.d.umn.edu/~tpederse/Pubs/cicling2002-b.pdf‎
    

    # Get the signatures for each synset.
    ss_sign1 = simple_signature(sense1,stem)
    ss_sign2 = simple_signature(sense2,stem)
    #print(ss_sign1)
    #print(ss_sign2)
    """
    score=0
    overlap=(set(ss_sign1[0])).intersection(ss_sign2[0])
    overlapped=list(filter(lambda a: (a in overlap) and (a not in list(string.punctuation)), ss_sign1[0]))
    score=len(overlapped)
    #print(set(ss_sign1[0]),set(ss_sign2[0]))
    if score!=0:
        print(set(ss_sign1[0]),overlapped,score)
    sim_score=0
    
    for ss1 in ss_sign1[1]:
        pos1=ss1.pos()
        if pos1=='v' or pos1=='n':
            for ss2 in ss_sign2[1]:
                pos2=ss2.pos()
                if pos1=='v':
                    path_score=ss1.path_similarity(ss2)
                    if path_score>=0.4:
                        #print(ss1.name(),ss2.name(),path_score)
                        sim_score+=path_score
                elif pos2=='n':                    
                    path_score=ss2.path_similarity(ss1)
                    if path_score>=0.4:
                        #print(ss1.name(),ss2.name(),path_score)
                        sim_score+=path_score
                    
            
    #print(score,sim_score) 
            
    return score+sim_score
    
    #return len(ss_sign1.intersection(ss_sign2))

emoDict={}
emotion=''
synsets=[]

positive=['happy']
negative=['sad','anger','disgust','fear']
surprise=['surprise']
emotions=positive+negative+surprise

with open('../data/emotion_dict_synsets.txt','r') as f:
        for line in f:
            line=line.strip()
            if line[0]=='-':
               if len(synsets)>0:
                   emoDict[emotion]=synsets
               synsets=[]
               emotion=line[1:]
            else:
                if emotion in positive:
                    synsets.append(simple_signature(line,wn.synset(line),'+'))
                elif emotion in negative:
                    synsets.append(simple_signature(line,wn.synset(line),'-'))
                else:
                    synsets.append(simple_signature(line,wn.synset(line),'+-'))
         
if len(synsets)>0:
    emoDict[emotion]=synsets




def calculateSimilarity(word,senses,pos,neg): 
    maxEmotionScore=0
    morphy=wn.morphy(word,senses['sense'].pos())
    if (word,'z') not in lexiconDict and (morphy is not None):
        word=morphy
    if lexiconDict[(word,'z')]=='+':
        emotionsToMatch=positive+surprise
        lexicon='+'
        for emotion in negative:
            senses[emotion]=0
    else:
        emotionsToMatch=negative+surprise
        lexicon='-'
        for emotion in positive:
            senses[emotion]=0

    sense=simple_signature(word,senses['sense'],lexicon)

    for emotion in emotionsToMatch:
        score=0
        max=0
        print(emotion)
        for synset in emoDict[emotion]:
            score+=similarity_lesk(synset,sense)
        if(score>max):
            max=score
        max=round(max,2)
        if(max>maxEmotionScore):
            maxEmotionScore=max
        senses[emotion]=max
    
    sense=senses['sense']
    #word=sense.name().split('.')[0]
    posTag=sense.pos()
    if posTag=='s':
        posTag='a'
    if (word,posTag) in lexiconDict:
        polarity=lexiconDict[(word,posTag)]
        if(polarity=='+'):
            pos=1
            neg=0
        else:
            pos=0
            neg=1
    elif (word,'z') in lexiconDict:
        polarity=lexiconDict[(word,'z')]
        if(polarity=='+'):
            pos=1
            neg=0
        else:
            pos=0
            neg=1
    #normalizing score between 0 and 1
    #polarity correction
    print("before RMS : " , senses,maxEmotionScore)
    if(maxEmotionScore!=0):
        maxEmotionScore+=1
        meanSquare=0
        for emotion in emotions:
            senses[emotion]=round(senses[emotion]/maxEmotionScore,2)
            if(senses[emotion]>0.5 and pos>neg and emotion in negative) or (senses[emotion]>0.5 and neg>pos and emotion in positive):
                senses[emotion]=1-senses[emotion]
            meanSquare+=(senses[emotion]**2)

        rootMeanSquare=math.sqrt(meanSquare)
        rootMeanSquare+=(0.25*rootMeanSquare)
        print("after polarity correction : ",senses,rootMeanSquare)
        if(rootMeanSquare>1):
            for emotion in emotions:
                senses[emotion]=round(senses[emotion]/rootMeanSquare,2)

    print("after RMS : " , senses)
    return senses
#to find similarity between two wordnet senses    
#print(similarity_lesk(wn.synset('anger.n.01'),wn.synset('angry.a.01')))