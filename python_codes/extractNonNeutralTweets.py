notNeutral=open('../data/Neutral2.txt','w')
notNeutralEmotions=open('../data/NeutralEmotions2.txt','w')
with open('../data/notNeutral.txt','r') as f, open('../data/notNeutralEmotions.txt','r') as fo:
    for tweet,emotion in zip(f,fo):
        tweet=tweet.strip()
        emotion=emotion.strip()
        if emotion=='neutral':
            notNeutral.write(tweet+'\n')
            notNeutralEmotions.write(emotion+'\n')