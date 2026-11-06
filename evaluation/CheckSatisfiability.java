package edu.clauseentailment;

//import com.opencsv.*;
//import com.opencsv.exceptions.CsvValidationException;
import java.io.*;
import java.util.*;
import java.util.regex.*;

import org.sat4j.specs.ContradictionException;
import org.sat4j.specs.IVecInt;

public class CheckSatisfiability {
	
	private final String input_fname;
	private final String output_fname;
	private final String instance;
	
	public CheckSatisfiability(final String input_dir, final String input_fname, final String output_fname, final String instance) {
		this.input_fname = input_dir + input_fname;
		this.output_fname = input_dir + output_fname;
		this.instance = instance;
	}
	
	// Parse a "remaining" string like "[[-1, 2], [-3, 2], [3, 1]]" into List<int[]>
    public static List<int[]> parseRemaining(String text) {
        List<int[]> result = new ArrayList<>();
        if (text == null) return result;
        // Regex to find inner bracket groups like [-1, 2]
        if (text.startsWith("[") && text.endsWith("]")) {
        	  text = text.substring(1, text.length() - 1);
        	}
        //System.out.println(text);
           
        Pattern p = Pattern.compile("\\[([^\\]]+)\\]");
        Matcher m = p.matcher(text);
        while (m.find()) {
            String inner = m.group(1);
            //System.out.println(inner);
            
            if (inner.isEmpty()) continue;
            String[] parts = inner.split(",");
            //System.out.println(Arrays.toString(parts));
            
            int[] clause = new int[parts.length];
            for (int i = 0; i < parts.length; i++) {
                String s = parts[i].trim();
                // handle possible leading/trailing non-numeric noise
                clause[i] = Integer.parseInt(s);
            }
            result.add(clause);
        }
        return result;
    }
    
    // Split on semicolons that are NOT inside square brackets
    public static List<String> splitRespectBrackets(String line) {
        List<String> parts = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        int bracketDepth = 0;
        for (int i = 0; i < line.length(); i++) {
            char ch = line.charAt(i);
            if (ch == '[') {
                bracketDepth++;
                current.append(ch);
            } else if (ch == ']') {
                // protect against negative depth in malformed lines
                if (bracketDepth > 0) bracketDepth--;
                current.append(ch);
            } else if (ch == ';' && bracketDepth == 0) {
                parts.add(current.toString());
                current.setLength(0);
            } else {
                current.append(ch);
            }
        }
        // add last part
        parts.add(current.toString());
        return parts;
    }
    
    public String ConcateArrayClauses (List<int[]> cls) {
    	if (cls.isEmpty()){
    		return "";
    	}
    	else {
    		String concat = new String();
    		for (int[] c : cls) {
    			concat = concat + Arrays.toString(c) + ",";
    		}
    		return concat.substring(0, concat.length() - 1);
    	}		
	}
    
    public int CheckCorrectness(int satisfiable, int obs_in_rem, int no_rem, String instance) {
    	if (instance == "POS") {
    		if (obs_in_rem == 1 && satisfiable == 1) {
    			return 1;
    		} else {
    			return 0;
    		}
    	} else {
    		if (satisfiable == 1 && obs_in_rem == 1 && no_rem == 1) {
    			return 1;
    		} else {
    			return 0;
    		}
    	}
    }
    
    public void process() throws IOException{
    	try (BufferedReader br = new BufferedReader(new FileReader(input_fname));
                PrintWriter pw = new PrintWriter(new FileWriter(output_fname))) {

               // Read header
               String header = br.readLine();
               if (header == null) {
                   System.err.println("Empty file.");
                   return;
               }

               // Write new header (keep same columns, add satisfiability)
               pw.println(header + ";satisfiable;muses;correct");

               String line;
               int lineNo = 1;
               while ((line = br.readLine()) != null) {
                   lineNo++;

                   // split respecting brackets
                   List<String> fields = splitRespectBrackets(line);
               
                   // Expect at least 7 fields: idx;remaining;num_atom;num_clauses;mus_set;prompt_tokens;output_tokens
                   if (fields.size() < 7) {
                       System.err.printf("Malformed line %d: expected >=7 fields but got %d. Line: %s%n",
                               lineNo, fields.size(), line);
                       // Option: skip or write with empty satisfiability
                       pw.println(line + ";"); // keep original and add empty value
                       continue;
                   }

                   // Trim fields
                   for (int i = 0; i < fields.size(); i++) {
                       fields.set(i, fields.get(i).trim());
                   }

                   String remaining = fields.get(3);    // e.g. [[-1, 2], [-3, 2], ...]
                   String numAtomsStr = fields.get(6);  // e.g. "5"
                   
                   int obs_in_rem = Integer.parseInt(fields.get(12)); 
                   int no_rem = Integer.parseInt(fields.get(13));
                   String idx = fields.get(0);
                   System.out.println("idx: " + idx);

                   // Parse num_atoms (safe)
                   int numAtoms = 0;
                   try {
                       numAtoms = Integer.parseInt(numAtomsStr);
                   } catch (NumberFormatException e) {
                       System.err.printf("Warning: cannot parse num_atoms at line %d: '%s'%n", lineNo, numAtomsStr);
                   }

                   // parse remaining into list of int[] clauses
                   List<int[]> clauses = parseRemaining(remaining);
                   List<IVecInt> AllMUSes = new ArrayList<IVecInt>();
                   List<int[]> row_mus = new ArrayList<int[]>();
                   var mainChecker = new ClauseEntailmentChecker_MUS(numAtoms);

                   // Sequentially apply checker for each clause and aggregate result
                   // Here we choose: satisfiability = 1 iff ALL checks return 1 (you can change logic)
                   int satisfiability = 1;
                   for (int[] clause : clauses) {
                   	try {
                   		//System.out.println(Arrays.toString(clause));
   						mainChecker.addClause(clause);
   					} catch (ContradictionException e) {
   						clauses.remove(clauses.size()-1);
   						System.out.println("remove the last clause");
   					} 
                   }
                   
                   if(mainChecker.isSatisfiable()) {
   						satisfiability = 1;
   					} else {
   					System.out.println(idx + " problem is unsatisfiable");
   					satisfiability = 0;
					try {
						AllMUSes = mainChecker.getListMUS();
						if (AllMUSes.size() > 1) {
							// flag = false;
							System.out.println("kebanyakan index");
						}	
					} 
					catch (ArrayIndexOutOfBoundsException e) {
						System.out.println("Failed to compute all MUSes.");
					}
					for (IVecInt mus : AllMUSes) {
						int[] indexes = mus.toArray();
						indexes = mainChecker.removeZeroIdxs(indexes);
						row_mus.add(indexes);
					}
   				   }
                   
                   // Reconstruct original (safe) fields joined by semicolon (preserve any extra fields)
                   StringBuilder outLine = new StringBuilder();
                   for (int i = 0; i < fields.size(); i++) {
                       if (i > 0) outLine.append(';');
                       outLine.append(fields.get(i));
                   }
                   outLine.append(';').append(satisfiability);
                   outLine.append(';').append(ConcateArrayClauses(row_mus));
                   
                   int corr = 0;
                   
                   corr = CheckCorrectness(satisfiability, obs_in_rem, no_rem, instance);
                   
                   outLine.append(';').append(corr);

                   pw.println(outLine.toString());
               } // end while
           } // end try-with-resources

           System.out.println("Processing complete. Output saved to: " + output_fname);
    	
    }
	
	public static void main(String[] args) throws IOException {
		if (args.length < 3) {
            System.out.println("Usage: java CheckSatisfiability <input_folder> <input_csv> <output_csv>");
            return;
        }
		new CheckSatisfiability(args[0], args[1], args[2], args[3]).process();  
    }
	
}