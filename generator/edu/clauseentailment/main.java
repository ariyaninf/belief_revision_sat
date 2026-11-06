package edu.clauseentailment;

import java.io.IOException;
import com.opencsv.exceptions.CsvValidationException;

public class main {

	public static void main(String[] args) throws IOException {
		//double[] probs = {0.01, 0.02, 0.03, 0.04, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5};
		double[] probs = {1};
		for (double i : probs) {
			int var = 15;
			int min_var = 6;
			int sat = 3;
			int cls = 26;
			int nset = 200;
			boolean mix_vars = false;
			boolean mix_clauses = false;
			String output_dir = "dataset/MUSes/3SAT_only/";
			double prob = i;
			
			var gs = new GenerateMUSes(var, min_var, sat, cls, nset, mix_vars, mix_clauses, output_dir, prob);
			gs.GenerateDataset();
			
	
			/*String[] arguments = new String[] {"dataset/Belief_Revision/3-SAT_only/deepseek-r1/", 
					"dimacs_PRED_NO_MUS_3satonly_6_fixVars_26_fixCls_100_1.0_500_OR_t3.csv", 
					"checked_PRED_NO_MUS_3satonly_6_fixVars_26_fixCls_100_1.0_500_OR_t3.csv",
					"NEG"};
			CheckSatisfiability.main(arguments);*/
			
			
		}
		
	}

}
