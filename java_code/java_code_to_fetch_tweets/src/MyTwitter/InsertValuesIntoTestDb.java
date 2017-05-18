package MyTwitter;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.PrintWriter;

public class InsertValuesIntoTestDb {

    @SuppressWarnings("rawtypes")
    public static void main(String[] args) throws Exception {
        String splitBy = ",";
        BufferedReader br = new BufferedReader(new FileReader("additionals/text_emotion.csv"));
        String filename2 = "additionals/train.txt";
		PrintWriter writer2 = new PrintWriter(filename2);
		writer2.print("");
		writer2.close();
		FileWriter fw2 = null;
		BufferedWriter bw2 = null;
		File file2 = new File(filename2);
		fw2 = new FileWriter(file2.getAbsoluteFile(), true);
		bw2= new BufferedWriter(fw2);
        String line = br.readLine();
        processTweets pt = new processTweets();
        String s;
        while((line = br.readLine())!=null){
             String[] b = line.split(splitBy);
            // System.out.println(b[3]);
             s=pt.processString(b[3]);
             bw2.write(s+"\n");
             
        }
        bw2.flush();
		bw2.close();
        br.close();
        
        

  }
}

