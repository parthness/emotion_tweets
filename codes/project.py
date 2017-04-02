import time, nltk, string
from nltk.tokenize import word_tokenize
from pywsd.lesk import adapted_lesk
from nltk.corpus import wordnet as wn
from lesk import calculateSimilarity
from senti_classifier.senti_classifier import synsets_scores
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordSenseDisambiguate import disambiguate
from preprocessTweet import preprocess


def notNeutral(sense):
    pos=sense['pos']
    neg=sense['neg']
    if(pos>neg or neg>pos):
        return True
    else:
        return False

nouns=['NN','NNP','NNS','NNPS']
verbs=['VB','VBD','VBG','VBN','VBP','VBZ']
adjectives=['JJ','JJR','JJS']
adverbs=['RB','RBR','RBS']

def wordnetScore(emotionalPart,namedEntities):

    #removing tokens other than nouns, verbs, adverbs, adjectives
    posToConsider=nouns+verbs+adverbs+adjectives
    pos_tokens=nltk.pos_tag(word_tokenize(emotionalPart))
    tokensToConsider=[]
    for token in pos_tokens:
        if token[1] in posToConsider and (token[0] not in namedEntities):
            tokensToConsider.append(token)

    t0_=time.time()
    #1.word sense disambiguation
    #senses={token[0]:token[1] for token in disambiguate(sentence) if (type(token[1])!=type(None) and token[0] not in namedEntities and notNeutral(dict(synsets_scores[token[1].name()])))}
    #senses={token[0]:token[1] for token in disambiguate(emotionalPart,namedEntities)}
    sensesInSentences,sentences=disambiguate(emotionalPart,namedEntities)
    if len(sensesInSentences)==0:
        print(emotionalPart, " - neutral")
    else:    
        print(sensesInSentences)
        print(sentences)
        #2.similarity calculation
        t1_=time.time()
        
        for index,sensesInSentence in enumerate(sensesInSentences):
            senses={}
            for wordSenseTuple in sensesInSentence:
                word=wordSenseTuple[0]
                sense=wordSenseTuple[1]
                senses[word]={}
                senses[word]['sense']=sense
                calculateSimilarity(senses[word],synsets_scores[sense.name()]['pos'],synsets_scores[sense.name()]['neg'])
            print(senses)
        print(time.time()-t1_,t1_-t0_)
    
def maxSentiment(sentiment):
    if sentiment['neu']>sentiment['pos'] and sentiment['neu']>sentiment['neg']:
        return 'neu'
    else:
        return 'sentimental'


#tweetsfile="../data/inputKeyword.txt"  
tweetsfile="../data/testinput.txt"
n=0
t0=time.time()
 

analyzer = SentimentIntensityAnalyzer()     
with open(tweetsfile,'r') as f:
    for tweet in f:
        sentences,sentenceType,namedEntities=preprocess(tweet)
        
        print(n,tweet)
        print(sentences)
        print(sentenceType)
        print(namedEntities)
        
        n+=1
        emotionalPart=''
        for index,sentence in enumerate(sentences):
            if sentenceType[index]!='?':# and maxSentiment(analyzer.polarity_scores(sentence+sentenceType[index]))!='neu':
                emotionalPart+=sentence+sentenceType[index]+' '
                
            else:
                print(sentence + ' --- neutral')
        if emotionalPart!='':
            wordnetScore(emotionalPart,namedEntities)
print(time.time()-t0)