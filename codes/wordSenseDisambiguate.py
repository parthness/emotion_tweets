import string
from itertools import chain

from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag
from pywsd.utils import lemmatize, synset_properties
from pywsd.utils import lemmatize_sentence
from senti_classifier.senti_classifier import synsets_scores
from nltk.stem.porter import *
from positive_negative_lexicon import lexiconDict
from nltk.tag.stanford import StanfordPOSTagger
from nltk.tokenize import TweetTokenizer

tweetTokenizer=TweetTokenizer()
path_to_model = '/Users/Parth/Desktop/emotion_tweet/codes/stanford-postagger-full-2016-10-31/models/english-bidirectional-distsim.tagger'
path_to_jar='/Users/Parth/Desktop/emotion_tweet/codes/stanford-postagger-full-2016-10-31/stanford-postagger-3.7.0.jar'
posTagger=StanfordPOSTagger(path_to_model, path_to_jar)

porter=PorterStemmer()
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

def compare_overlaps(context, synsets_signatures):
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

    # Returns only the best sense.
    return ranked_synsets[0][1]


def simple_signature(ambiguous_word, pos=None):
    """
    Returns a synsets_signatures dictionary that includes signature words of a
    sense from its:
    (i)   definition
    (ii)  example sentences
    (iii) hypernyms and hyponyms
    """
    synsets_signatures = {}

    synsets=wn.synsets(ambiguous_word,pos)
    if len(synsets)==0:
        synsets=wn.synsets(ambiguous_word)
    
    for ss in synsets:

        signature = []
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
        signature+= list(chain(*[i.lemma_names() for i in ss_hypohypernyms]))
        
        signature = [i for i in signature if i not in EN_STOPWORDS]
        # Lemmatized context is preferred over stemmed context.
        signature = [lemmatize(i) for i in signature]
        # Matching exact words may cause sparsity, so optional matching for stems.
        signature = [porter.stem(i) for i in signature]
        
        synsets_signatures[ss] = signature

    return synsets_signatures

def simple_lesk(emotionalPart, ambiguous_word, pos):
    """
    Simple Lesk is somewhere in between using more than the
    original Lesk algorithm (1986) and using less signature
    words than adapted Lesk (Banerjee and Pederson, 2002)
    """

    # Get the signatures for each synset.
    ss_sign = simple_signature(ambiguous_word, pos)

    context_sentence=lemmatize_sentence(emotionalPart)
   
    best_sense = compare_overlaps(context_sentence, ss_sign)
    return best_sense

apostrophes=["n't","'d","'ll","'s","'m","'ve","'re","na"]
stopwords = stopwords.words('english')[:-19] + list(string.punctuation) + apostrophes

def notNeutral(word,sense,pos):
    '''
    #wordsIncorrectInSentiWordNet=["glad","thank"]
    if word in disgustingWords:#+wordsIncorrectInSentiWordNet:
        print(word)
        return True
    pos=sense['pos']
    neg=sense['neg']
    if(pos>0.125 or neg>0.125) and pos!=neg:
        return True
    else:
        return False
    '''
    morphy=wn.morphy(word,pos)
    if morphy is not None:
        if (morphy,pos) in lexiconDict or (morphy,'z') in lexiconDict:
            return True

    if (word,pos) in lexiconDict or (word,'z') in lexiconDict or word in disgustingWords:
        return True
    else:
        return False
    
def correctSense(synsetsList,lemma):    
    '''
    for synset in synsetsList:
        if synset.name().split('.')[0]==lemma:
            return synset
    '''
    #print(lemma, synsetsList)
    if len(synsetsList)>0:
        return synsetsList[0]
    return None

def disambiguate(emotionalPart, namedEntities):
    '''
    tagged_sentence = []
    # Pre-lemmatize the sentnece before WSD
    
    surface_words, lemmas, morphy_poss = lemmatize_sentence(emotionalPart, keepWordPOS=True)
        
    for word, lemma, pos in zip(surface_words, lemmas, morphy_poss):
        if lemma not in stopwords: # Checks if it is a content word
            if word not in namedEntities: 
                try:
                    wn.synsets(lemma)[0]
                    synset = simple_lesk(emotionalPart, lemma, pos=pos)
                except: # In case the content word is not in WordNet
                    synset = '#NOT_IN_WN#'
            else:
                synset = '#NAMED#'
        else:
            synset = '#STOPWORD/PUNCTUATION'
        
        tagged_sentence.append((word, synset))

    # Change #NOT_IN_WN# and #STOPWORD/PUNCTUATION# into None.
    
    print("tagged_sentence : ",tagged_sentence)

    sentences=[]
    sentence=[]
    formed_sentences=[]
    formed_sentence=' '

    for word,tag in tagged_sentence:
        if not (str(tag).startswith('#') and str(tag).endswith('#')): #NOT_IN_WN#, #NAMED#
            if str(tag).startswith('#'):
                if word in ['.','?','!']:
                    if len(sentence)>0:
                        sentences.append(sentence)
                        sentence=[]
                        formed_sentences.append(formed_sentence)
                    formed_sentence=' '
                else:
                    formed_sentence+=word + ' '
            elif notNeutral(word,dict(synsets_scores[tag.name()]),tag.pos()): 
            #else: 
                sentence.append((word,tag))
                formed_sentence+=word + ' '
            else:
                formed_sentence+=word + ' '
    '''
    sentences=[]
    sentence=[]
    formed_sentences=[]
    formed_sentence=' '
    '''
    print(lemmatize_sentence)
    words, lemmas, pos = lemmatize_sentence(emotionalPart, keepWordPOS=True)
    print(words,lemmas,pos,lemmatize_sentence(emotionalPart))
    for index,lemma in enumerate(lemmas):
        if pos[index]!=None:
            if words[index] not in namedEntities:
                if lemma not in stopwords:
                    print(lemma,pos[index])
                    sense=correctSense(wn.synsets(lemma,pos=pos[index]),lemma)
                    if type(sense)==type(None):
                        sense=correctSense(wn.synsets(lemma),lemma)
                    if type(sense)!=type(None):
                        #sense=sense[0]
                        if notNeutral(lemma,dict(synsets_scores[sense.name()]),pos[index]):
                            sentence.append((words[index],sense))
                        formed_sentence+=words[index]+ ' '
                else:
                    formed_sentence+=words[index]+' '
        elif lemma in ['.','!','?']:
            if len(sentence)>0:
                sentences.append(sentence)
                sentence=[]
                formed_sentences.append(formed_sentence)
            formed_sentence=' '
        else:
            formed_sentence+=words[index]+' '
    '''
    #our implementation from here
    pronouns=["I","We","You","They","He","She","It","i","we","you","they","he","she","it"]
    posTags=posTagger.tag(tweetTokenizer.tokenize(emotionalPart))
    print(posTags)
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
                        elif notNeutral(word.lower(),dict(synsets_scores[sense.name()]),pos):
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