package MyTwitter;

public class processTweets {
	String inputStr;	
	
	public String processString(String st){
		inputStr = st;
		// Replace here 2nd parameter by "USERID "
		inputStr = inputStr.replaceAll("@[A-Za-z0-9:@]*", "USER");
		//to check whether all links are replaced or not.
		
		// Replace here 2nd parameter by "URL "
		inputStr = inputStr.replaceAll("(((((http[s]?|ftp):/)/?(?:www.)?)|(www\\.))[^ \\.]+\\.[^ ]{2,}|www\\.[^ ]+\\.[^ ]{2,})","");
		//System.out.println("###" + inputTweet);
		inputStr = inputStr.replaceAll("\n"," . ");
		
		return inputStr;
	}
}
