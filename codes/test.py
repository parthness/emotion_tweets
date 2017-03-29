import string
from nltk.tokenize import word_tokenize
'''
punctuations=list(string.punctuation)
dict={}
n=1
with open('final_dict_slangs.txt','r') as f:
    for slang in f:
        slang=slang.split(':')
        key=slang[0].strip()
        value=slang[1].strip()
        dict[key]=value



w=open('final_dict_slangs.txt','w')
with open('dict_apostrophe.txt','r') as f:
    for slang in f:
        slang=slang.split(':')
        key=slang[0].strip()
        value=slang[1].strip()
        dict[key]=value

for key,value in dict.items():
    w.write(key+":"+value+'\n')
w.close()

n=0
with open('dict_apostrophe.txt','r') as f:
    for slang in f:
        slang=slang.split(':')
        if slang[0].strip() not in dict:
            print(slang[0])
        print(n)
        n+=1

'''
import nltk 
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize

sample="World Banks CEO Praised Modis Decision of Demonetization"

sentences = nltk.sent_tokenize(sample)
tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names

entity_names = []
for tree in chunked_sentences:
    entity_names.extend(extract_entity_names(tree))

print(entity_names)

st = StanfordNERTagger('/Users/Parth/Desktop/project_docs/codes/stanford-ner-2016-10-31/classifiers/english.muc.7class.distsim.crf.ser.gz',
					   '/Users/Parth/Desktop/project_docs/codes/stanford-ner-2016-10-31/stanford-ner.jar',
					   encoding='utf-8')

tokenized_text = word_tokenize(sample)
classified_text = st.tag(tokenized_text)

entities_list=[]
for entity in entity_names:
    entities_list+=entity.split()
    
for tuple in classified_text:
    if tuple[1]!='O':
        entities_list.append(tuple[0])

for entity in (set(entities_list)):
    print(entity)
