import time, nltk, string, math
from nltk.tokenize import word_tokenize
from pywsd.lesk import adapted_lesk
from nltk.corpus import wordnet as wn
from lesk import calculateSimilarity
from senti_classifier.senti_classifier import synsets_scores
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordSenseDisambiguate import disambiguate
from preprocessTweet import preprocess
from lexicon import lexiconDict

positive=['happy']
negative=['sad','anger','disgust','fear']
emotions=positive+negative+['surprise']
outputAmans=open('../data/outputAmansFile.txt',"w")

def findMaxEmotionList(finalEmotion):
    maxEmotionList=[]
    for emotion in emotions:
        if finalEmotion[emotion]>=0.5:
            maxEmotionList.append(emotion)

    return maxEmotionList

def findMaxEmotion(senses):
    max=-1
    for emotion in emotions:
        if senses[emotion]>max:
            max=senses[emotion]

    return max

def notNeutral(sense):
    pos=sense['pos']
    neg=sense['neg']
    if(pos>neg or neg>pos):
        return True
    else:
        return False
'''
nouns=['NN','NNP','NNS','NNPS']
verbs=['VB','VBD','VBG','VBN','VBP','VBZ']
adjectives=['JJ','JJR','JJS']
adverbs=['RB','RBR','RBS']
'''
negators=['neither','not','never','nor','no','none']
positiveIntensifiers=['especially','exceptionally','excessively','extremely','extraordinarily',\
                      'definitely','very','perfectly','nicely','surely','more','mostly','most','pretty','really']
negativeIntensifiers=['rarely','barely','moderately','slightly','less','hardly']

def fuzzyUnion(senses):
    finalEmotion={}
    maxScore=-1
    maxEmotion=''
    for word,scores in senses.items():
        for emotion in emotions:
            if emotion in finalEmotion and senses[word][emotion]>finalEmotion[emotion]:
                finalEmotion[emotion]=senses[word][emotion]
            elif emotion not in finalEmotion:
                finalEmotion[emotion]=senses[word][emotion]
            if finalEmotion[emotion]>maxScore:
                maxScore=finalEmotion[emotion]
                maxEmotion=emotion
    if maxScore<=0.4:
        maxEmotion='neutral'
    return finalEmotion, maxEmotion


def wordnetScore(emotionalPart,namedEntities):
    '''
    #removing tokens other than nouns, verbs, adverbs, adjectives
    posToConsider=nouns+verbs+adverbs+adjectives
    pos_tokens=nltk.pos_tag(word_tokenize(emotionalPart))
    tokensToConsider=[]
    for token in pos_tokens:
        if token[1] in posToConsider and (token[0] not in namedEntities):
            tokensToConsider.append(token)
    '''
    t0_=time.time()
    #1.word sense disambiguation
    #senses={token[0]:token[1] for token in disambiguate(sentence) if (type(token[1])!=type(None) and token[0] not in namedEntities and notNeutral(dict(synsets_scores[token[1].name()])))}
    #senses={token[0]:token[1] for token in disambiguate(emotionalPart,namedEntities)}
    sensesInSentences,sentences=disambiguate(emotionalPart,namedEntities)
    if len(sensesInSentences)==0:
        print(emotionalPart, " - neutral")
        return 'neutral',['neutral']
    else:    
        print(sensesInSentences)
        print(sentences)
        #2.similarity calculation
        t1_=time.time()
        fuzzyUnionSentences={}
        for index,sensesInSentence in enumerate(sensesInSentences):
            senses={}
            for wordSenseTuple in sensesInSentence:
                word=wordSenseTuple[0]
                sense=wordSenseTuple[1]
                senses[word]={}
                senses[word]['sense']=sense
                calculateSimilarity(word,senses[word],synsets_scores[sense.name()]['pos'],synsets_scores[sense.name()]['neg'])
                #negators and Intensifiers
            print(senses)
            negatorPresent=False
            positiveIntensifierPresent=False
            negativeIntensifierPresent=False
            for token in sentences[index].split():
                if token in negators:
                    negatorPresent=True
                elif token in positiveIntensifiers:
                    positiveIntensifierPresent=True
                elif token in negativeIntensifiers:
                    negativeIntensifierPresent=True
                elif token in senses:
                    if positiveIntensifierPresent:
                        maxEmotionScore=findMaxEmotion(senses[token])
                        for emotion in emotions:
                            prevScore=senses[token][emotion]
                            if senses[token][emotion]>=0.5 or senses[token][emotion]==maxEmotionScore:
                                senses[token][emotion]=round(math.sqrt(senses[token][emotion]),2)
                            else:
                                senses[token][emotion]=round(senses[token][emotion]**2,2)
                            if negatorPresent:
                                senses[token][emotion]=math.sqrt(prevScore*senses[token][emotion])
                        if negatorPresent:
                            negatorPresent=False
                        positiveIntensifierPresent=False
                    if negativeIntensifierPresent:
                        maxEmotionScore=findMaxEmotion(senses[token])
                        for emotion in emotions:  
                            prevScore=senses[token][emotion]                              
                            if senses[token][emotion]>0.5 or senses[token][emotion]==maxEmotionScore:
                                senses[token][emotion]=round(senses[token][emotion]**2,2)
                            else:
                                senses[token][emotion]=round(math.sqrt(senses[token][emotion]),2)
                            if negatorPresent:
                                senses[token][emotion]=math.sqrt(prevScore*senses[token][emotion])
                        if negatorPresent:
                            negatorPresent=False
                        negativeIntensifierPresent=False
                    if negatorPresent:
                        lemma=senses[token]['sense'].lemmas()[0]
                        antonym=lemma.antonyms()
                        oppositeEmotion=''
                        if len(antonym)>0:
                            antonymDict={}
                            sense=wn.lemma_from_key(antonym[0].key()).synset()
                            antonymDict['sense']=sense
                            antonymWord=sense.name().split('.')[0]
                            if (antonymWord,'z') in lexiconDict:
                                senses[token]=calculateSimilarity(antonymWord,antonymDict,synsets_scores[sense.name()]['pos'],synsets_scores[sense.name()]['neg'])
                        else:    
                            for emotion in emotions:
                                if senses[token][emotion]>0.5:
                                    senses[token][emotion]=round(1-senses[token][emotion],2)
                        negatorPresent=False

            print(senses)    
            finalEmotion, maxEmotion=fuzzyUnion(senses)
            fuzzyUnionSentences[sentences[index]]=finalEmotion

        finalEmotion, maxEmotion=fuzzyUnion(fuzzyUnionSentences)
        maxEmotionList=findMaxEmotionList(finalEmotion)
        

        print(finalEmotion)
        print(time.time()-t1_,t1_-t0_)
        return maxEmotion, maxEmotionList

def maxSentiment(sentiment):
    if sentiment['neu']>sentiment['pos'] and sentiment['neu']>sentiment['neg']:
        return 'neu'
    else:
        return 'sentimental'

#tweetsfile="../data/inputKeyword.txt"  
tweetsfile="../data/notNeutral.txt"
errorFile=open("../data/errors2.txt",'w')
accuracy={'happy':{'tp':0,'tn':0,'fp':0,'fn':0},'sad':{'tp':0,'tn':0,'fp':0,'fn':0},'anger':{'tp':0,'tn':0,'fp':0,'fn':0},
        'disgust':{'tp':0,'tn':0,'fp':0,'fn':0},'surprise':{'tp':0,'tn':0,'fp':0,'fn':0},'fear':{'tp':0,'tn':0,'fp':0,'fn':0},
        'neutral':{'tp':0,'tn':0,'fp':0,'fn':0}}
n=1
t0=time.time()
score=0
analyzer = SentimentIntensityAnalyzer()     
with open(tweetsfile,'r') as f, open('../data/notNeutralEmotions.txt','r') as fo:
    for tweet,emotion in zip(f,fo):
        sentences,sentenceType,namedEntities=preprocess(tweet)
        emotion=emotion.strip()
        print(n,tweet)
        print(sentences)
        print(sentenceType)
        print(namedEntities)
        maxEmotion='neutral'
        n+=1
        emotionalPart=''
        for index,sentence in enumerate(sentences):
            #if sentenceType[index]!='?':# and maxSentiment(analyzer.polarity_scores(sentence+sentenceType[index]))!='neu':
            emotionalPart+=sentence+sentenceType[index]+' '               
            #else:
            #    print(sentence + ' --- neutral')
            #    maxEmotion='neutral'
        if emotionalPart!='':
            maxEmotion, maxEmotionList=wordnetScore(emotionalPart,namedEntities)
        outputAmans.write(maxEmotion+'\n')
        if emotion in maxEmotionList:
            score+=1
            accuracy[emotion]['tp']+=1
            for other in emotions+['neutral']:
                if other!=emotion:
                    accuracy[other]['tn']+=1
        else:
            errorFile.write(str(n-1) + tweet + "   Aman's value : " + emotion + "  Our value : " + maxEmotion+ "\n")
            accuracy[emotion]['fn']+=1
            accuracy[maxEmotion]['fp']+=1
        print("score : " , score)
print(time.time()-t0)
n-=1
print("accuracy : ",score*100/n)
print(accuracy)

errorFile.close()
outputAmans.close()