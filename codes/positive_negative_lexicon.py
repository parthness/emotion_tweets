datafile='../data/negative_words.txt'
lexiconDict={}

with open(datafile,'r') as f:
    for line in f:
        line=line.strip()
        lexiconDict[(line,'z')]='-'

datafile='../data/positive_words.txt'
with open(datafile,'r') as f:
    for line in f:
        line=line.strip()
        lexiconDict[(line,'z')]='+'