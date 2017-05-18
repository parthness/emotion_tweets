import time, nltk, string, math
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet as wn
from lesk import calculateSimilarity
from wordSenseDisambiguate import disambiguate
from preprocessTweet import preprocess
from positive_negative_lexicon import lexiconDict
import numpy as np
import matplotlib.pyplot as plt

positive=['happy']
negative=['sad','anger','disgust','fear']
emotions=positive+negative+['surprise']
outputAmans=open('../data/outputAmansFile.txt',"w")

def findMaxEmotionList(finalEmotion):
    maxEmotionList=[]
    for emotion in emotions:
        if finalEmotion[emotion]>=0.5:
            maxEmotionList.append(emotion)
    
    if len(maxEmotionList)==0:
        maxEmotionList.append('neutral')
    
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
                      'definitely','very','perfectly','nicely','surely','more','mostly','most','pretty','really','much','such','quite']
negativeIntensifiers=['rarely','barely','moderately','slightly','less','hardly','could','would']

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
        finalEmotion={'happy':0,'sad':0,'anger':0,'disgust':0,'fear':0,'surprise':0}
        return 'neutral',finalEmotion
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
                calculateSimilarity(word,senses[word])
                #negators and Intensifiers
            print("before Intensifiers and negators", senses)
            negatorPresent=False
            positiveIntensifierPresent=False
            negativeIntensifierPresent=False
            for token in sentences[index].split():
                if token in negators:
                    negatorPresent=not negatorPresent
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
                        print(antonym)
                        antonymFound=False
                        if len(antonym)>0:
                            antonymDict={}
                            sense=wn.lemma_from_key(antonym[0].key()).synset()
                            antonymDict['sense']=sense
                            antonymWord=sense.name().split('.')[0]
                            print(antonymWord, antonymWord in lexiconDict)
                            if antonymWord in lexiconDict:
                                antonymFound=True
                                senses[token]=calculateSimilarity(antonymWord,antonymDict)
                        #else:
                        if not antonymFound:    
                            for emotion in emotions:
                                if senses[token][emotion]>0.5:
                                    senses[token][emotion]=round(1-senses[token][emotion],2)
                        negatorPresent=False

            print("after Intensifiers and negators", senses)    
            finalEmotion, maxEmotion=fuzzyUnion(senses)
            fuzzyUnionSentences[sentences[index]]=finalEmotion

        finalEmotion, maxEmotion=fuzzyUnion(fuzzyUnionSentences)
        
        print(finalEmotion)
        print(time.time()-t1_,t1_-t0_)
        return maxEmotion, finalEmotion


def test(tweetsfile,errorFile,correctEmotionFile):
    #tweetsfile="../data/inputKeyword.txt"  
    errorFile=open(errorFile,'w')
    scoreFile=open('../data/scoresOurs.txt','w')
    accuracy={'happy':{'tp':0,'tn':0,'fp':0,'fn':0},'sad':{'tp':0,'tn':0,'fp':0,'fn':0},'anger':{'tp':0,'tn':0,'fp':0,'fn':0},
            'disgust':{'tp':0,'tn':0,'fp':0,'fn':0},'surprise':{'tp':0,'tn':0,'fp':0,'fn':0},'fear':{'tp':0,'tn':0,'fp':0,'fn':0},
            'neutral':{'tp':0,'tn':0,'fp':0,'fn':0}}
    n=1
    t0=time.time()
    score=0
         
    with open(tweetsfile,'r') as f, open(correctEmotionFile,'r') as fo:
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
                #if sentenceType[index]!='?':
                emotionalPart+=sentence+sentenceType[index]+' '               
                #else:
                #    print(sentence + ' --- neutral')
                #    maxEmotion='neutral'
            if emotionalPart!='':
                maxEmotion, finalEmotion=wordnetScore(emotionalPart,namedEntities)
                maxEmotionList=findMaxEmotionList(finalEmotion)
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
            scoreFile.write(str(n-1)+" : " + str(score)+"\n")
    print(time.time()-t0)
    n-=1
    print("accuracy : ",score*100/n)
    print(accuracy)

    errorFile.close()
    outputAmans.close()


def plotGraph(emotionScores,title):
    emotionColor={'happy':'#f4f269','sad':'#4286f4','anger':'#ef3e32','disgust':'#ea0edb','fear':'#0eea83','surprise':'#ea8a0e'}
    numOfEmotions=len(emotions)
    bars=[emotionScores[emotion]*100 for emotion in emotions]
    color=[emotionColor[emotion] for emotion in emotions]

    ind = np.arange(numOfEmotions)    # the x locations for the groups
    width = 0.4       # the width of the bars: can also be len(x) sequence

    p1 = plt.barh(ind, bars, width, color=color)

    plt.ylabel('Emotions')
    plt.xlabel('Score')
    plt.title(title)
    plt.yticks(ind, ('happy', 'sad', 'anger', 'disgust', 'fear', 'surprise'))
    plt.xticks(np.arange(0, 110, 10))

    plt.show()


def run(inputFile,outputFile):
    n=1
    emotionalTweets=0
    numTweets={'happy':0,'sad':0,'anger':0,'disgust':0,'fear':0,'surprise':0}
    numTweetsEmotions=0
    with open(inputFile,'r') as f:
        for tweet in f:
            sentences,sentenceType,namedEntities=preprocess(tweet)
            print(n,tweet)
            print(sentences)
            print(sentenceType)
            print(namedEntities)
            n+=1
            emotionalPart=''

            for index,sentence in enumerate(sentences):
                if sentenceType[index]!='?':
                    emotionalPart+=sentence+sentenceType[index]+' '
            
            if emotionalPart!='':
                maxEmotion, finalEmotion=wordnetScore(emotionalPart,namedEntities)
                if maxEmotion!='neutral':
                    maxEmotionList=findMaxEmotionList(finalEmotion)
                    if 'neutral' in maxEmotionList:
                        maxEmotion='neutral'
            else:
                maxEmotion='neutral'
                maxEmotionList=['neutral']

            if maxEmotion!='neutral':
                emotionalTweets+=1
                for emotion in maxEmotionList:
                    numTweets[emotion]+=1
                    numTweetsEmotions+=1
    if numTweetsEmotions!=0:
        for emotion,score in numTweets.items():
            numTweets[emotion]=numTweets[emotion]/numTweetsEmotions

    print(str(emotionalTweets)+" were emotional out of " + str(n-1) + " extracted tweets")
    print("emotional content in " + str(emotionalTweets) + " tweets")
    print(numTweets)
    graphTitle="emotional content in " + str(emotionalTweets)+" out of " + str(n-1) + " extracted tweets"
    plotGraph(numTweets,graphTitle)

def runSingleTweet(tweet):
    sentences,sentenceType,namedEntities=preprocess(tweet)
    emotionalPart=''

    for index,sentence in enumerate(sentences):
        if sentenceType[index]!='?':
            emotionalPart+=sentence+sentenceType[index]+' '
    
    if emotionalPart!='':
        maxEmotion, finalEmotion=wordnetScore(emotionalPart,namedEntities)
    else:
        finalEmotion={'happy':0,'sad':0,'anger':0,'disgust':0,'fear':0,'surprise':0}

    graphTitle='scores for ' + tweet
    plotGraph(finalEmotion,graphTitle)

'''
tweetsfile='../data/Neutral.txt'
errorFile='../data/errorsNeutralFinal.txt'
correctEmotionFile='../data/neutralEmotions.txt'
test(tweetsfile,errorFile,correctEmotionFile)
'''

inputFile='../data/sampleTweesData/Nirbhaya.txt'
outputFile='../data/outputtest.txt'
run(inputFile,outputFile)

'''
inp=''
while inp!='exit':
    inp=input('enter tweet or exit : ')
    if inp!='exit':
        runSingleTweet(inp)

'''