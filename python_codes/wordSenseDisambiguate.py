import string
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag
from positive_negative_lexicon import lexiconDict
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize import TweetTokenizer

tweetTokenizer=TweetTokenizer()
path_to_model = '/Users/Parth/Desktop/Analysing_tweets_for_emotion_detection/python_codes/stanford-postagger-full-2016-10-31/models/english-bidirectional-distsim.tagger'
path_to_jar='/Users/Parth/Desktop/Analysing_tweets_for_emotion_detection/python_codes/stanford-postagger-full-2016-10-31/stanford-postagger-3.7.0.jar'
posTagger=StanfordPOSTagger(path_to_model, path_to_jar)

EN_STOPWORDS = stopwords.words('english')
disgustingWords=["fucked-up", "fucking", "disgusting", "ridiculous", "awful", "awkward", \
                     "gross", "shitty", "bullshit", "vulgar", "unforgivable", "intolerable", "hated", "disgust", \
                     "terrible", "fuck", "ass", "asshole", "revulsion", "loathing", "nausea", "detestation", \
                     "antipathy", "degrade", "humiliate", "disgrace", "shameful"]
nouns=['NN','NNP','NNS','NNPS']
verbs=['VB','VBD','VBG','VBN','VBP','VBZ']
adjectives=['JJ','JJR','JJS']
adverbs=['RB','RBR','RBS']
posToConsider=nouns+verbs+adjectives+adverbs

apostrophes=["n't","'d","'ll","'s","'m","'ve","'re","na"]
stopwords = stopwords.words('english')[:-19] + list(string.punctuation) + apostrophes

def notNeutral(word,pos):
    morphy=wn.morphy(word,pos)
    if morphy is not None:
        if morphy in lexiconDict or morphy in lexiconDict:
            return True

    if word in lexiconDict or word in disgustingWords:
        return True
    else:
        return False
    
def correctSense(synsetsList,lemma):    
    #print(lemma, synsetsList)
    if len(synsetsList)>0:
        return synsetsList[0]
    return None

def disambiguate(emotionalPart, namedEntities):
    sentences=[]
    sentence=[]
    formed_sentences=[]
    formed_sentence=' '

    #our implementation from here
    pronouns=["I","We","You","They","He","She","It","i","we","you","they","he","she","it"]
    posTags=posTagger.tag(tweetTokenizer.tokenize(emotionalPart))
    #print(posTags)
    for index,wordPosTuple in enumerate(posTags):
        word=wordPosTuple[0]
        pos=wordPosTuple[1]
        if pos in posToConsider:
            pos=pos[0].lower()
            if pos=='j':
                pos='a'
            if word not in namedEntities:
                if word not in stopwords:
                    print(word,pos)
                    sense=correctSense(wn.synsets(word,pos=pos),word)
                    if type(sense)==type(None):
                        sense=correctSense(wn.synsets(word),word)
                    if type(sense)!=type(None):
                        #sense=sense[0]
                        if word.lower() in ['like']:
                            if(index-1>=0):
                                if posTags[index-1][0] not in ['be','is','am','are','was','were']:
                                    sentence.append((word.lower(),wn.synset('like.v.03')))
                        elif notNeutral(word.lower(),pos):
                            sentence.append((word.lower(),sense))
                        formed_sentence+=word.lower()+ ' '
                else:
                    formed_sentence+=word.lower()+' '
        elif word in ['.','!','?']:
            if len(sentence)>0:
                sentences.append(sentence)
                sentence=[]
                formed_sentences.append(formed_sentence)
            formed_sentence=' '
        else:
            formed_sentence+=word+' '
    
    return sentences, formed_sentences