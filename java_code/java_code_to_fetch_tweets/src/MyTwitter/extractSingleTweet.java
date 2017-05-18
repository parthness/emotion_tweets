package MyTwitter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import twitter4j.Query;
import twitter4j.QueryResult;
import twitter4j.Status;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.conf.ConfigurationBuilder;

public class extractSingleTweet {
	
	public static void main(String[] args) throws TwitterException {

		//twitter account credentials
		ConfigurationBuilder cb = new ConfigurationBuilder();
		cb.setDebugEnabled(true).
		setOAuthConsumerKey("***YOUR CONSUMER KEY***").
		setOAuthConsumerSecret("***YOUR CONSUMER SECRET***").
		setOAuthAccessToken("***YOUR ACCESS TOKEN***").
		setOAuthAccessTokenSecret("***YOUR ACCESS TOKEN SECRET***");
		
		TwitterFactory tf = new TwitterFactory(cb.build());
		twitter4j.Twitter twitter = tf.getInstance();
		
		//giving keyword or hashtag and containing only tweets no retweet
		
		Query query = new Query("#nishu"+ "+exclude:retweets");
		query.setLang("en");
		
		int numberOfTweets = 40;
		List<Status> tweetList = new ArrayList<Status>();
		List<Status> temp = new ArrayList<Status>();
		Long minId = Long.MAX_VALUE;
		

		//QueryResult result = twitter.search(query); 
		// searchWithRetry is my function that deals with rate limits		
		int finish=0;
		while(tweetList.size() < numberOfTweets && finish!=1){
			
			if (numberOfTweets - tweetList.size() > 90)
			      query.setCount(90);
			    else{
			      query.setCount(numberOfTweets - tweetList.size());
			      finish=1;
			    }
		    try {
		      QueryResult result = twitter.search(query);
		     // taking tweets in batch and adding to our final list
		      temp=result.getTweets();
		      if(temp.size() == 0){
		    	  break;
		      }
		      tweetList.addAll(temp);
		      System.out.println("Gathered " + tweetList.size() + " tweets");
		      for (Status t: tweetList) 
		        if(t.getId() < minId) minId = t.getId();
	
		    }
	
		    catch (TwitterException te) {
		      System.out.println("Couldn't connect: " + te);
		    }; 
		    query.setMaxId(minId-1);
			
		}

		System.out.println("total tweets : "+tweetList.size());
		processTweets pt = new processTweets();
		
		
			for(int i=0 ; i<tweetList.size() ;i++){
				Status t=tweetList.get(i);
				System.out.println("##~~ Without preprocessing ~~##:\t " + t.getText());
				String inputTweet = t.getText().replaceAll("[^\\x00-\\x7F]", "");
				inputTweet = pt.processString(inputTweet);
				System.out.println("##~~ With preprocessing ~~##:\t " + inputTweet);	
			}
				
	}
}
