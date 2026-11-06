package edu.clauseentailment;

import java.io.IOException;
import com.opencsv.exceptions.CsvValidationException;

public class main {

	public static void main(String[] args) throws IOException {
					
			String dataset_path = "";
			String dimacs_file = ""; //the dimacs file name (.csv)
			String output_file = ""; //the output file name (.csv)
			String data_mode = ""; //"POS" for MUS (unsatisfiable) dataset, and "NEG" for NO_MUS (satisfiable) dataset 
			
	
			String[] arguments = new String[] {dataset_path, 
					dimacs_file, 
					output_file,
					data_mode};
			CheckSatisfiability.main(arguments);
		
	}

}
