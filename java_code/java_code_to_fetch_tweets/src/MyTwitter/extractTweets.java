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
import twitter4j.Query;
import twitter4j.QueryResult;
import twitter4j.Status;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.conf.ConfigurationBuilder;

public class extractTweets {
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
		//emotion = {anger , sad, happy, disgust , fear , surprise};
		String emotion = "anger";
		List<String> emotionWords = new ArrayList<String>();
		HashSet<String> hs = new HashSet<>();
		String emotionFile="emotion/"+emotion+".txt";
		try (BufferedReader br = new BufferedReader(new FileReader(emotionFile))) {
		    String line;
		    while ((line = br.readLine()) != null) {
		       // process the line.
		    	emotionWords.add("#"+line.toLowerCase());
		    }
		    	hs.addAll(emotionWords);
				emotionWords.clear();
				emotionWords.addAll(hs);   
		}catch(FileNotFoundException ex){
			ex.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		int counter =0;
		HashSet<String> hs2 = new HashSet<>();
		List<String> processedTweets = new ArrayList<String>();
		int numberOfTweets = 800;
		List<Status> tweetList = new ArrayList<Status>();
		List<Status> temp = new ArrayList<Status>();
		Long minId = Long.MAX_VALUE;
		int finish=0;
		String filename = "additionals/"+emotion+".txt";
		System.out.println("Writing into file : "+filename+" with "+emotionWords.size()+" words");
		for(counter = 0 ; counter < emotionWords.size() ; counter++){	
				hs2.clear();
				processedTweets.clear();
				tweetList.clear();
				Query query = new Query(emotionWords.get(counter)+ "+exclude:retweets");
				query.setLang("en");
				
				finish=0;
				//QueryResult result = twitter.search(query); 
				// searchWithRetry is my function that deals with rate limits		
				
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
					
					hs2.addAll(processedTweets);
					processedTweets.clear();
					processedTweets.addAll(hs2);
					
						//System.out.println("##~~## " + processedTweets.get(i));
						BufferedWriter bw = null;
						FileWriter fw = null;
				
						try {
				
							File file = new File(filename);
				
							// true = append file
							fw = new FileWriter(file.getAbsoluteFile(), true);
							bw = new BufferedWriter(fw);
							for(int i=0 ; i<processedTweets.size() ;i++){
								bw.write(processedTweets.get(i)+"\n");
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
				System.out.println("File done for "+emotion+"with emotion hashtag"+emotionWords.get(counter));
	
		}
		System.out.println("Done for only writing. Now removing redundant.");
		removeRedundant rr = new removeRedundant();
		rr.remove(filename);
		System.out.println("Done finally !!  file : "+filename);
	}
}
