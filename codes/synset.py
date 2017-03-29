from nltk.corpus import wordnet as wn
dict={}
w=open("../data/synsets.txt",'w')

with open("../data/wordnet_similarity_emotions.txt",'r') as f:
	for entry in f:
		inputs=[]
		entry=entry.split(':')
		synsets=[]
		print(entry[0])
		w.write(entry[0]+'\n')
		for synset in entry[1].split(','):
			synset=synset.strip()
			wn_synsets=wn.synsets(synset)
			if len(wn_synsets)>0:
				print("***"+synset+"***")
				for syn in wn_synsets:
					print(syn.definition())
				index=input("required synset : ")
				synsets.append(wn_synsets[int(index)])
				inputs.append(index)
		dict[entry[0]]=synsets
		
		for inp in inputs:
			w.write(inp+'\n')

w.close()