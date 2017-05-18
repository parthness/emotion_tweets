from nltk import pos_tag as posTag

emotions=['happy','sad','anger','disgust','surprise','fear']

for emotion in emotions:
	with open("trainingData/" + emotion + ".txt") as f:
		for tweet in f:
			