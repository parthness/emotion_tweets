package ShufflingFile;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class shuffleFile {
	public static void main(String[] args){
		
		
		List<String> processedTweets = new ArrayList<String>();
		String filename = "additionals/fear.txt"; 
		try (BufferedReader br = new BufferedReader(new FileReader(filename))) {
		    String line;
		    while ((line = br.readLine()) != null) {
		       // process the line.
		    	processedTweets.add(line);
		    }
				Collections.shuffle(processedTweets);
				System.out.println("total processed tweets after reading from file : "+processedTweets.size());
				PrintWriter writer = new PrintWriter(filename);
				writer.print("");
				writer.close();
					
					BufferedWriter bw = null;
					BufferedWriter bw2 = null;
					FileWriter fw = null;
					FileWriter fw2 = null;
					
					try {
						String filename2 = "randomFiles/fear.txt";
						PrintWriter writer2 = new PrintWriter(filename2);
						writer2.print("");
						writer2.close();
						File file = new File(filename);
						File file2 = new File(filename2);
						// true = append file
						fw = new FileWriter(file.getAbsoluteFile(), true);
						fw2 = new FileWriter(file2.getAbsoluteFile(), true);
						bw = new BufferedWriter(fw);
						bw2= new BufferedWriter(fw2);
						int i;
						for(i=0 ; i<processedTweets.size() ;i++){
							bw.write(processedTweets.get(i)+"\n");
							if( i < 10000){
								//System.out.println(i);
								bw2.write(processedTweets.get(i)+"\n");
							}
						}
						//System.out.println(i);
					} catch (IOException e) {
			
						e.printStackTrace();
			
					} finally {
			
						try {
			
							if (bw != null) {
								bw.flush();
								bw2.flush();
								bw.close();
								bw2.close();
							}
			
							if (fw != null){
								fw.close();
								fw2.close();
							}
							
			
						} catch (IOException ex) {
			
							ex.printStackTrace();
			
						}
					
			}
		    
		}catch(FileNotFoundException ex){
			ex.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	
	}
}
