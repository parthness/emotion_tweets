package MyTwitter;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

public class removeRedundant {
	public void remove(String filename){
		//Remove redundant from the file having processed text.
		
		HashSet<String> hs = new HashSet<>();
		List<String> processedTweets = new ArrayList<String>();
		
		try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
		    String line;
		    while ((line = br.readLine()) != null) {
		       // process the line.
		    	processedTweets.add(line);
		    }
		    	hs.addAll(processedTweets);
				processedTweets.clear();
				processedTweets.addAll(hs);
				System.out.println("total processed tweets after reading from file : "+processedTweets.size());
				PrintWriter writer = new PrintWriter(filename);
				writer.print("");
				writer.close();
				for(int i=0 ; i<processedTweets.size() ;i++){
					
					BufferedWriter bw = null;
					FileWriter fw = null;
			
					try {
			
						File file = new File(filename);
			
						// true = append file
						fw = new FileWriter(file.getAbsoluteFile(), true);
						bw = new BufferedWriter(fw);
			
						bw.write(processedTweets.get(i)+"\n");
			
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
			}
		    
		}catch(FileNotFoundException ex){
			ex.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	
}
