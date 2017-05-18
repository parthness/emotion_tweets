package MyTwitter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;

import twitter4j.Paging;
import twitter4j.Query;
import twitter4j.QueryResult;
import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.conf.ConfigurationBuilder;

public class extractInputTweets {
	
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
		
		String inputFile="inputKeyword";
		String hashtag="#NirbhayaGetsJustice";		//hashtag to be searched		
		HashSet<String> hs = new HashSet<>();
		List<String> processedTweets = new ArrayList<String>();
		int numberOfTweets = 2000;
		List<Status> tweetList = new ArrayList<Status>();
		List<Status> temp = new ArrayList<Status>();
		Long minId = Long.MAX_VALUE;
		int finish=0;
		String filename = "additionals/"+inputFile+".txt";
		System.out.println("Writing into file : "+filename+" with  "+ hashtag +"  words");
		//TwitterFactory tf2 = new TwitterFactory(cb.build());
		//twitter4j.Twitter unauthenticatedTwitter = tf2.getInstance();
		//First param of Paging() is the page number, second is the number per page (this is capped around 200 I think.
		//Paging paging = new Paging(1, 100);
		//List<Status> statuses = unauthenticatedTwitter.getUserTimeline("@nishu2901",paging);
		Query query = new Query(hashtag + "+exclude:retweets");
		query.setLang("en");
		
		finish=0;
		//QueryResult result = twitter.search(query); 
		// searchWithRetry is my function that deals with rate limits		
		tweetList.clear();
		while(tweetList.size() < numberOfTweets && finish!=1){
			
			if (numberOfTweets - tweetList.size() > 95)
			      query.setCount(95);
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
		      //System.out.println("Gathered " + tweetList.size() + " tweets");
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
			
			String inputTweet = t.getText().replaceAll("[^\\x00-\\x7F]", "");
			inputTweet = pt.processString(inputTweet);
			processedTweets.add(inputTweet);
		}
		
		hs.addAll(processedTweets);
		processedTweets.clear();
		processedTweets.addAll(hs);
		
		//System.out.println("##~~## " + processedTweets.get(i));
		BufferedWriter bw = null;
		FileWriter fw = null;

		try {

			File file = new File(filename);

			// true = append file
			fw = new FileWriter(file.getAbsoluteFile(), false);
			bw = new BufferedWriter(fw);
			for(int i=0 ; /*i<statuses.size()*/ i < processedTweets.size() ;i++){
				bw.write(processedTweets.get(i)+"\n");
				//bw.write(statuses.get(i).getText()+"\n");
			}
		} catch (IOException e) {

			e.printStackTrace();

		} finally {

			try {

				if (bw != null)
					bw.close();

				if (fw != null)
					fw.close();
			} catch (IOException ex) {

				ex.printStackTrace();

			}
		}
		System.out.println("File done for "+inputFile+"with input hashtag"+ hashtag);
	
	
		System.out.println("Done for only writing. Now removing redundant.");
		removeRedundant rr = new removeRedundant();
		rr.remove(filename);
		System.out.println("Done finally !!  file : "+filename);
	}
}
