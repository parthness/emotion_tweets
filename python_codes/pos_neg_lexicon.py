datafile='../data/negative-words.txt'
lexiconDict={}

with open(datafile,'r') as f:
	for line in f:
		line=line.strip()
		lexiconDict[(line,'z')]='-'