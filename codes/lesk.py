#!/usr/bin/env python -*- coding: utf-8 -*-
#
# Python Word Sense Disambiguation (pyWSD)
#
# Copyright (C) 2014-2017 alvations
# URL:
# For license information, see LICENSE.md
import math
from itertools import chain

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from senti_classifier.senti_classifier import synsets_scores
from pywsd.utils import lemmatize, porter, synset_properties

EN_STOPWORDS = stopwords.words('english')

def compare_overlaps(context, synsets_signatures, \
                     nbest=False, keepscore=False, normalizescore=False):
    """
    Calculates overlaps between the context sentence and the synset_signture
    and returns a ranked list of synsets from highest overlap to lowest.
    """
    overlaplen_synsets = [] # a tuple of (len(overlap), synset).
    for ss in synsets_signatures:
        overlaps = set(synsets_signatures[ss]).intersection(context)
        overlaplen_synsets.append((len(overlaps), ss))

    # Rank synsets from highest to lowest overlap.
    ranked_synsets = sorted(overlaplen_synsets, reverse=True)

    # Normalize scores such that it's between 0 to 1.
    if normalizescore:
        total = float(sum(i[0] for i in ranked_synsets))
        ranked_synsets = [(i/total,j) for i,j in ranked_synsets]

    if not keepscore: # Returns a list of ranked synsets without scores
        ranked_synsets = [i[1] for i in sorted(overlaplen_synsets, \
                                               reverse=True)]

    if nbest: # Returns a ranked list of synsets.
        return ranked_synsets
    else: # Returns only the best sense.
        return ranked_synsets[0]

def simple_signature(ss, stem=False):
    """
    Returns a synsets_signatures dictionary that includes signature words of a
    sense from its:
    (i)   definition
    (ii)  example sentences
    (iii) hypernyms and hyponyms
    """
    signature=[]
   # print("ss: ",ss)
    # Includes definition.
    ss_definition = synset_properties(ss, 'definition')
    signature+=word_tokenize(ss_definition)
    # Includes examples
    ss_examples = synset_properties(ss, 'examples')
    signature+=list(chain(*[i.split() for i in ss_examples]))
    # Includes lemma_names.
    ss_lemma_names = synset_properties(ss, 'lemma_names')
    signature+= ss_lemma_names
    # Optional: includes lemma_names of hypernyms and hyponyms.
    
    ss_hyponyms = synset_properties(ss, 'hyponyms')
    ss_hypernyms = synset_properties(ss, 'hypernyms')
    ss_hypohypernyms = ss_hypernyms+ss_hyponyms
    signature += list(chain(*[i.lemma_names() for i in ss_hypohypernyms]))
  #  print(signature)
    '''
    # Includes holonyms.
    ss_mem_holonyms = synset_properties(ss, 'member_holonyms')
    ss_part_holonyms = synset_properties(ss, 'part_holonyms')
    ss_sub_holonyms = synset_properties(ss, 'substance_holonyms')
    # Includes meronyms.
    ss_mem_meronyms = synset_properties(ss, 'member_meronyms')
    ss_part_meronyms = synset_properties(ss, 'part_meronyms')
    ss_sub_meronyms = synset_properties(ss, 'substance_meronyms')
    # Includes similar_tos
    ss_simto = synset_properties(ss, 'similar_tos')
    
    related_senses = list(set(ss_mem_holonyms+ss_part_holonyms+
                              ss_sub_holonyms+ss_mem_meronyms+
                              ss_part_meronyms+ss_sub_meronyms+ ss_simto))

    signature += list([j for j in chain(*[synset_properties(i, 'lemma_names')
                                         for i in related_senses])
                      if j not in EN_STOPWORDS])
  #  print(signature)
    # Optional: removes stopwords.
    '''
    signature = [i for i in signature if i.lower() not in EN_STOPWORDS]
    # Lemmatized context is preferred over stemmed context.
    signature = [lemmatize(i) for i in signature]
    # Matching exact words may cause sparsity, so optional matching for stems.
    if stem == True:
        signature = [porter.stem(i) for i in signature]

    return signature


def similarity_lesk(sense1, sense2, \
                stem=False):
    """
    This function is the implementation of the Adapted Lesk algorithm,
    described in Banerjee and Pederson (2002). It makes use of the lexical
    items from semantically related senses within the wordnet
    hierarchies and to generate more lexical items for each sense.
    see www.d.umn.edu/~tpederse/Pubs/cicling2002-b.pdf‎
    """

    # Get the signatures for each synset.
    ss_sign1 = simple_signature(sense1,stem)
    ss_sign2 = simple_signature(sense2,stem)
    #print(ss_sign1)
    #print(ss_sign2)
    overlap=set(ss_sign1).intersection(ss_sign2)
    #print(overlap)
    score = len(overlap)
    sim1=[]
    sim2=[]
    for ss in ss_sign1:
        synsets=wn.synsets(ss,pos='n')
        if len(synsets)>0:
            if synsets[0] not in sim1:
                synset=synsets[0] 
                '''
                pos=synsets_scores[synset.name()]['pos']
                neg=synsets_scores[synset.name()]['neg']
                if(pos>neg or neg>pos): 
                '''
                sim1.append(synset)
    for ss in ss_sign2:
        synsets=wn.synsets(ss,pos='n')
        if len(synsets)>0:
            if synsets[0] not in sim2:
                synset=synsets[0] 
                '''
                pos=synsets_scores[synset.name()]['pos']
                neg=synsets_scores[synset.name()]['neg']
                if(pos>neg or neg>pos): 
                '''
                sim2.append(synset)
    sim_score=0
    for ss1 in sim1:
      #  pos1=ss1.name().split('.')[1]
      #  if pos1=='v' or pos1=='n':
            for ss2 in sim2:
       #         pos2=ss2.name().split('.')[1]
        #        if pos1=='v':
                    path_score=ss1.path_similarity(ss2)
                    if path_score>=0.4:
                        #print(ss1.name(),ss2.name(),path_score)
                        sim_score+=path_score
         #       elif pos2=='v' or pos2=='n':
                    path_score=ss2.path_similarity(ss1)
                    if path_score>=0.4:
                        #print(ss1.name(),ss2.name(),path_score)
                        sim_score+=path_score
            
    #print(score,sim_score)         
    return score+math.ceil(sim_score)

#to find similarity between two wordnet senses    
#print(similarity_lesk(wn.synset('anger.n.01'),wn.synset('angry.a.01')))