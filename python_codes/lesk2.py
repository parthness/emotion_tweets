from nltk.corpus import wordnet as wn

emoDict={}
emotion=''
synsets=[]
positive=['happy']
negative=['sad','anger','disgust','fear']
surprise=['surprise']
emotions=positive+negative+surprise

with open('../data/emotion_dict_synsets2.txt','r') as f:
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
print(emoDict)
def mostRelatedNounSense(word,posTag):
    synsets=wn.synsets(word,posTag)
    lemmas=[]
    drfs=[]
    for synset in synsets:
        for lemma in synset.lemmas():
            lemmas.append(lemma)

    for lemma in lemmas:
        for drf in lemma.derivationally_related_forms():
            if drf.synset().pos()=='n':
                drfs.append(drf)

    words=[lemma.name() for lemma in drfs]
    wordSynset={lemma.name():lemma.synset() for lemma in drfs}
    lenWords=len(words)

    result=[(w,float(words.count(w))/lenWords) for w in set(words)]
    result.sort(key=lambda w : w[-1])

    if len(result)>0:
        return wordSynset[result[len(result)-1][0]]
    else:
        return None


def calculateSimilarity(word,senses,pos,neg): 
    maxEmotionScore=0
    sense=senses['sense']
    posTag=senses['sense'].pos()
    if posTag!='n':
        mostRelatedNoun=mostRelatedNounSense(word,posTag)
    else:
        mostRelatedNoun=sense
    if type(mostRelatedNoun)==type(None):
        for emotion in emotions:
            senses[emotion]=0
        return senses
    else:
        for emotion in emotions:
            score=0
            max=0
            print(emotion)
            for synset in emoDict[emotion]:
                score=synset.wup_similarity(mostRelatedNoun)
                if(score>max):
                    max=score
            max=round(max,2)
            if(max>maxEmotionScore):
                maxEmotionScore=max
            senses[emotion]=max

        if(maxEmotionScore!=0):
            maxEmotionScore+=1
            for emotion in emotions:
                if(senses[emotion]>0.5 and pos>neg and emotion in negative) or (senses[emotion]>0.5 and neg>pos and emotion in positive):
                    senses[emotion]=1-senses[emotion]

        return senses