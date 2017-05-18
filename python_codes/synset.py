from nltk.corpus import wordnet as wn
dict={}
w=open("../data/synsets.txt",'w')

with open("../data/wordnet_similarity_emotions2.txt",'r') as f:
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
					print(syn.name(), syn.definition())
				index=input("required synset : ")
				sense=wn_synsets[int(index)]
				synsets.append(sense)
				w.write(sense.name()+'\n')
		dict[entry[0]]=list(set(synsets))
		
w.close()