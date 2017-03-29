import re, time, enchant, nltk, string
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from collections import Counter
from pywsd.lesk import adapted_lesk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from lesk import similarity_lesk
from senti_classifier import senti_classifier
from senti_classifier.senti_classifier import synsets_scores
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pywsd import disambiguate
from preprocessTweet import preprocess

def calculateSimilarity(senses):
    emotions=['happy','sad','anger','disgust','fear','surprise']
    sense=senses['sense']
    print(sense)
    for emotion in emotions:
        score=0
        max=0
        for synset in emoDict[emotion]:
            score=similarity_lesk(synset,sense)
            if(score>max):
                max=score
        senses[emotion]=round(max,2)


def wordnetScore(sentence,namedEntities):

    nouns=['NN','NNP','NNS','NNPS']
    verbs=['VB','VBD','VBG','VBN','VBP','VBZ']
    adjectives=['JJ','JJR','JJS']
    adverbs=['RB','RBR','RBS']

    #removing tokens other than nouns, verbs, adverbs, adjectives
    posToConsider=nouns+verbs+adverbs+adjectives
    pos_tokens=nltk.pos_tag(word_tokenize(sentence))
    tokensToConsider=[]
    for token in pos_tokens:
        if token[1] in posToConsider and (token[0] not in namedEntities):
            tokensToConsider.append(token)

    t0_=time.time()
    #1.word sense disambiguation
    senses={token[0]:token[1] for token in disambiguate(sentence) if type(token[1])!=type(None)}
    #2.similarity calculation
    t1_=time.time()

    for word,sense in senses.items():
        senses[word]={}
        senses[word]['sense']=sense
        calculateSimilarity(senses[word])
    print(senses)
    print(time.time()-t1_,t1_-t0_)

def maxSentiment(sentiment):
    if sentiment['neu']>sentiment['pos'] and sentiment['neu']>sentiment['neg']:
        return 'neu'
    else:
        return 'sentimental'


#tweetsfile="../data/inputKeyword.txt"  
tweetsfile="../data/testinput.txt"
n=1
t0=time.time()
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

analyzer = SentimentIntensityAnalyzer()     
with open(tweetsfile,'r') as f:
    for tweet in f:
        sentences,sentenceType,namedEntities=preprocess(tweet)
        print(n,tweet)
        print(sentences)
        print(sentenceType)
        print(namedEntities)
        n+=1
        
        for index,sentence in enumerate(sentences):
            if sentenceType[index]!='?' and maxSentiment(analyzer.polarity_scores(sentence))!='neu':
                wordnetScore(sentence,namedEntities)
print(time.time()-t0)