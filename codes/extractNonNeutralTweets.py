notNeutral=open('../data/notNeutral.txt','w')
notNeutralEmotions=open('../data/notNeutralEmotions.txt','w')
with open('../data/testinput.txt','r') as f, open('../data/AmansDatasetRefined/emotionCategoryGold.txt','r') as fo:
    for tweet,emotion in zip(f,fo):
        tweet=tweet.strip()
        emotion=emotion.strip()
        if emotion!='neutral':
            notNeutral.write(tweet+'\n')
            notNeutralEmotions.write(emotion+'\n')