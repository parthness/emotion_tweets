import re, time, enchant, nltk, string
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from collections import Counter
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

EN_STOPWORDS = stopwords.words('english')

dictSlang={}
with open('../data/final_dict_slangs.txt','r') as slangFile:
    for slang in slangFile:
        slang=slang.split(':')
        dictSlang[slang[0].strip()]=slang[1].strip()

def words(text): 
    return re.findall(r'\w+', text.lower())


WORDS = Counter(words(open('../data/corpus.txt').read()))


def prob(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N


def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
    return entity_names


def named_entities(sentence):
   # print(sentence)
    sentences = nltk.sent_tokenize(sentence)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
    entity_names = []

    for tree in chunked_sentences:
        entity_names.extend(extract_entity_names(tree))
    '''
    st = StanfordNERTagger('/Users/Parth/Desktop/project_docs/codes/stanford-ner-2016-10-31/classifiers/english.muc.7class.distsim.crf.ser.gz',
                           '/Users/Parth/Desktop/project_docs/codes/stanford-ner-2016-10-31/stanford-ner.jar',
                           encoding='utf-8')

    tokenized_text = word_tokenize(sentence)
    classified_text = st.tag(tokenized_text)

    entities_list=[]
    for entity in entity_names:
        entities_list+=entity.split()
        
    for tuple in classified_text:
        if tuple[1]!='O':
            entities_list.append(tuple[0])
    
    return list(set(entities_list))
    '''
    entities_list=[]
    for entity in entity_names:
        if ' ' in entity:
            for subentity in entity.split():
                entities_list.append(subentity)
        else:
            entities_list.append(entity)
    return list(set(entities_list))


def splitHashtag(hashtag):
    uppercase=re.compile("[A-Z]")
    lowercase=re.compile("[a-z]")
    digit=re.compile("[0-9]")
    
    if len(hashtag)==0:
        return '#'
    if '_' in hashtag:
        return ' '.join(hashtag.split('_'))
    else:
        splittedHashtag=hashtag[0]
        for char in hashtag[1:]:
            if (uppercase.match(char)!=None and uppercase.match(splittedHashtag[-1])==None) or (digit.match(char)!=None and digit.match(splittedHashtag[-1])==None): 
                splittedHashtag+=' '+char
            elif lowercase.match(char) and uppercase.match(splittedHashtag[-1])!=None and len(splittedHashtag[:-1])>0:
                splittedHashtag=splittedHashtag[:-1]+' '+splittedHashtag[-1]+char
            else:
                splittedHashtag+=char

    return ' '.join(splittedHashtag.split())


def spellCorrect(spell,dictionary):
    
    suggestions=dictionary.suggest(spell)
    if len(suggestions)==0:
        return ' ' #incorrect spelling - to be removed
    probabilities={prob(suggestion):suggestion for suggestion in suggestions}
    return probabilities[max(probabilities)]


def preprocess(tweet): #dict - dictionary of slangs
    tweet=tweet.strip()
    # hashtag split
    tokens=[token if token[0]!='#' else splitHashtag(token[1:]) for token in tweet.split()]
    if '#' in tokens:
        tokens.remove('#')
    tweet=' '.join(tokens)
        
    sentences=re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', tweet)    
    sentences=[sentence.strip() for sentence in sentences]

    notSentence=re.compile("^[\?\.\!' ]+$") #to eliminate sentences having only punctuations
    sentenceType=[] 
    filteredSentences=[] 
    punctuations=['.','?','!']
    pronouns=["I","We","You","They","He","She","It"]
    apostrophes=["n't","'d","'ll","'s","'m","'ve","'re","na"]
    namedEntities=named_entities(tweet)
    print(namedEntities)
    digit=re.compile("[0-9]")
    repeatedLetters=re.compile(r"(.)\1{2,}")
    abbreviations=re.compile("^[A-Z\.]+$")
    dictionary=enchant.Dict("en_US")
 
    for sentence in sentences:
        if notSentence.match(sentence)==None and len(sentence)>0:
            #detect type of sentence
            punctuation=sentence[-1]
            while sentence[-1] in punctuations:
                sentence=sentence[:-1]
            sentence=sentence.strip()
            if punctuation not in punctuations:
                punctuation='.' 
            #spell check
            sentenceTokens=[]
            for token in word_tokenize(sentence):
                if len(token.strip())>0:
                    sentenceTokens.append(token.strip())
            numOfCorrected=0
            correctedTokens=[]
            if punctuation!='?':
                for index,token in enumerate(sentenceTokens):
                    #  print(token)
                    if (token in (list(string.punctuation))) or digit.search(token)!=None:
                        correctedTokens.append(token)
                    else:
                        if (token not in pronouns+namedEntities) and abbreviations.match(token)==None and dictionary.check(token)!=True:
                            token=token.lower()
                        if dictionary.check(token) or ((index+1)<len(sentenceTokens) and sentenceTokens[index+1] in apostrophes):
                            correctedTokens.append(token)
                        elif token in apostrophes and len(correctedTokens)>0:
                            key=(correctedTokens[-1]+token).lower()
                            if key in dictSlang:
                                correctedTokens[-1]=dictSlang[key]
                            else:
                                correctedTokens[-1]=correctedTokens[-1]+token
                        elif token in dictSlang:
                            correctedTokens.append(dictSlang[token])
                        elif token.lower() in dictSlang and token in namedEntities:
                            correctedTokens.append(dictSlang[token.lower()])
                            namedEntities.remove(token)
                        else:
                            repeatedLettersMatch=repeatedLetters.search(token)
                            while repeatedLettersMatch!=None:
                                toBeReplaced=repeatedLettersMatch.group(0)
                                replaceWith=toBeReplaced[0]+toBeReplaced[0]
                                token=re.sub(toBeReplaced,replaceWith,token)
                                repeatedLettersMatch=repeatedLetters.search(token)
                            if dictionary.check(token) or token in namedEntities or abbreviations.match(token)!=None:
                                correctedTokens.append(token)
                            else:
                                if '-' in token:
                                    subtokens=token.split('-')
                                    for subtoken in subtokens:
                                        if len(subtoken.strip())>0:
                                            if dictionary.check(subtoken):
                                                correctedTokens.append(subtoken)
                                            else:
                                                correctedTokens.append(spellCorrect(subtoken,dictionary))
                                                numOfCorrected+=1
                                else:
                                    correctedTokens.append(spellCorrect(token,dictionary))
                                    numOfCorrected+=1
                if ' ' in correctedTokens:
                    correctedTokens.remove(' ') 
                if numOfCorrected<=(0.5*len(correctedTokens)):
                    filteredSentences.append(' '.join(correctedTokens))
                    sentenceType.append(punctuation)
            else:
                filteredSentences.append(sentence)
                sentenceType.append(punctuation)

    return filteredSentences,sentenceType,namedEntities