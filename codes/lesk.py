import math
from itertools import chain
import string
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from positive_negative_lexicon import lexiconDict
from wordSenseDisambiguate import disgustingWords
from pywsd.utils import synset_properties, lemmatize

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

    ss_definition = synset_properties(ss, 'definition')
    signature+=word_tokenize(ss_definition)

    ss_lemma_names = synset_properties(ss, 'lemma_names')
    signature+= ss_lemma_names
    
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
            if word not in lexiconDict and morphy not in lexiconDict:
                to_remove.append(word)
        else:
            if word in lexiconDict:
                if lexiconDict[word]!=lexicon:
                    to_remove.append(word)
            elif (morphy is not None) and morphy in lexiconDict:
                if lexiconDict[morphy]!=lexicon:
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
                pos=synset.pos()
                morphy=wn.morphy(ss,pos)
                if ss in lexiconDict or ss in lexiconDict or ss in disgustingWords:
                    sim.append(synset)
                elif (morphy is not None) and (morphy in lexiconDict or morphy in lexiconDict):
                    sim.append(synset)
                else:
                    signature.remove(ss)
        else:
            signature.remove(ss)
    return [signature,sim]


def similarity_lesk(ss_sign1, ss_sign2):
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
            
    return score+sim_score

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


def calculateSimilarity(word,senses): 
    maxEmotionScore=0
    morphy=wn.morphy(word,senses['sense'].pos())
    if word not in lexiconDict and (morphy is not None):
        word=morphy
    if lexiconDict[word]=='+':
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

    print("before RMS : " , senses,maxEmotionScore)
    if(maxEmotionScore!=0):
        maxEmotionScore+=1
        meanSquare=0
        for emotion in emotions:
            senses[emotion]=round(senses[emotion]/maxEmotionScore,2)
            meanSquare+=(senses[emotion]**2)

        rootMeanSquare=math.sqrt(meanSquare)
        rootMeanSquare+=(0.25*rootMeanSquare)
        print("RMS : ",senses,rootMeanSquare)
        if(rootMeanSquare>1):
            for emotion in emotions:
                senses[emotion]=round(senses[emotion]/rootMeanSquare,2)

    print("after RMS : " , senses)
    return senses
