package edu.clauseentailment;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

import org.sat4j.specs.ContradictionException;
import org.sat4j.specs.IVecInt;

public class GenerateMUSes {
	
	private final int NVAR;
	private final int MIN_NVAR;
	private static int KSAT;
	private final int NCLAUSE;
	private final int MIN_NCLAUSE;
	private int NUMSET;
	private int VARPOS;
	private int VARNEG;
	private boolean IS_MIXVARS;
	private boolean IS_MIXCLAUSES;
	private final String fname;
	private final String output_dir;
	private static final int[] EMPTY_CLAUSE = {};
	private static double PROBABILITY;
	
	
	public GenerateMUSes(final int i_nvar, final int i_minvar, final int i_ksat, final int i_nclause, final int i_numset, final boolean is_MixVars, 
			final boolean is_MixClauses, final String output_dir, double i_prob) {
		this.NVAR = i_nvar;
		this.MIN_NVAR = i_minvar; //25
		GenerateMUSes.KSAT = i_ksat;
		this.NCLAUSE = i_nclause;
		this.MIN_NCLAUSE = 10; //15
		this.NUMSET = i_numset;
		this.VARPOS = 0;
		this.VARNEG = 0;
		this.IS_MIXVARS	= is_MixVars;
		this.IS_MIXCLAUSES = is_MixClauses;
		this.output_dir = output_dir;
		GenerateMUSes.PROBABILITY = i_prob;
		
		if (!this.IS_MIXVARS && !this.IS_MIXCLAUSES) {
			this.fname = this.output_dir + "MUS_" + KSAT + "sat_" + NVAR + "_fixVars_" + NCLAUSE + "_fixCls_" + NUMSET + "_" + i_prob + ".csv";
		} else if (!this.IS_MIXVARS && this.IS_MIXCLAUSES) {
			this.fname = this.output_dir + "MUS_" + KSAT + "sat_" + NVAR + "_fixVars_" + NCLAUSE + "_mixCls_" + NUMSET + "_" + i_prob + ".csv";
		} else if (this.IS_MIXVARS && !this.IS_MIXCLAUSES) {
			this.fname = this.output_dir + "MUS_" + KSAT + "sat_" + NVAR + "_mixVars_" + NCLAUSE + "_fixCls_" + NUMSET + "_" + i_prob + ".csv";
		} else {
			this.fname = this.output_dir + "MUS_" + KSAT + "sat_" + NVAR + "_mixVars_" + NCLAUSE + "_mixCls_" + NUMSET + "_" + i_prob + ".csv";
		}
	
	}
	
	public int RandomLiteral(int NVAR) {
		int randomNum = 0;
		while(randomNum == 0) {
			randomNum = ThreadLocalRandom.current().nextInt(- NVAR, NVAR);
		}
		return randomNum;
	}
	
	public boolean IsExists (int[] clause1, List<int[]> clauses) {
		boolean flag = false;
		Arrays.sort(clause1);
		for (int[] elem : clauses) {
			Arrays.sort(elem);
			if (Arrays.equals(clause1, elem)) {
				flag = true;
			}
		}
		return flag;
	}
	
	public static int generateRandomSATWithProbability() {
        double randomValue = Math.random();
        switch (KSAT) {
        case 2:
        	if (randomValue < PROBABILITY) {
                return 1;
            } else {
                return 2;
            }
        case 3:
        	if (randomValue < 0.3) {
                return 1;
            } else if (randomValue >= 0.3 && randomValue < 0.7){
                return 2;
            } else {
            	return 3;
            }
        }
		return 0;        
    }
	
	public int[] GenerateRule (int NVAR, List<int[]> clauses) {
		// int len_sat = ThreadLocalRandom.current().nextInt(2, KSAT + 1); //uncomment this to mix the SAT
		// int len_sat = generateRandomSATWithProbability(); //uncomment this to mix the SAT with random Probability
		int len_sat = KSAT;  //uncomment this fix the SAT
		
		int[] clause = new int[len_sat];
		boolean is_exists = true;
		
		int hitung = 0;
		
		while (is_exists) {
			hitung += 1;
			int vpos = 0;
			int vneg = 0;
			
			for (int j=0; j < len_sat; j++) {
				int flag = 1;
				while (flag == 1) {
					flag = 0;
					int lit = RandomLiteral(NVAR);
					if (lit > 0) {
						vpos += 1;
					} else {vneg += 1;}
					
					for (int element : clause) {
					    if (Math.abs(element) == Math.abs(lit)) {
					        flag = 1;
					    }
					}
					
					if (flag == 0) {
						clause[j] = lit;
					}
					
				}
			}
			
			is_exists = IsExists(clause, clauses);
			
			if (!is_exists) {
				VARPOS = VARPOS + vpos;
				VARNEG = VARNEG + vneg;
			}
			
			if (hitung > 100) {
				return EMPTY_CLAUSE;
			}
		}
		return clause;
	}
	
	public String ConcateArrayClauses (List<int[]> cls) {
		String concat = new String();
		for (int[] c : cls) {
			concat = concat + Arrays.toString(c) + ",";
		}
		return concat.substring(0, concat.length() - 1);
	}
	
	public void GenerateDataset() {
		int id = 0;
		int numClauses = 0;
		int numVars = 0;
		
		try {
			PrintWriter writer = new PrintWriter(fname, "UTF-8");	
			writer.println("id;clauses;mus_indices;num_vars;num_clauses;label;mus_set");
			
			while(id < NUMSET) {
				writer.flush();
				/* HINT: Initiate the number of clauses */
				if (IS_MIXCLAUSES) {
					numClauses = ThreadLocalRandom.current().nextInt(MIN_NCLAUSE, NCLAUSE + 1);
				} else {
					numClauses = NCLAUSE;
				}
				
				/* HINT: Initiate the number of variables */
				if (IS_MIXVARS) {
					numVars = ThreadLocalRandom.current().nextInt(MIN_NVAR, NVAR + 1);
				} else {
					numVars = NVAR;
				}
								
				List<int[]> clauses = new ArrayList<int[]>();
				List<IVecInt> AllMUSes = new ArrayList<IVecInt>();
				List<int[]> row_mus = new ArrayList<int[]>();
				var mainChecker = new ClauseEntailmentChecker_MUS(numVars);
				boolean flag = true;
				
				/* Generate rules for premises and feed them to the solver in Dimacs format */
				while (clauses.size() < numClauses) {
					int[] clause = new int[KSAT];
					clause = GenerateRule(numVars, clauses);
					
					if (clause.length == 0) {
						//clause is empty
						flag = false;
						System.out.println("clause is empty");						
					}
					
					clauses.add(clause);
		
					try {
						mainChecker.addClause(clause);
						
					} catch (ContradictionException e) {
						flag = false;
						clauses.remove(clauses.size()-1);
						System.out.println("remove the last clause");
					} 
			
				}
								
				if(!mainChecker.isSatisfiable() && flag) {
					try {
						AllMUSes = mainChecker.getListMUS();
						if (AllMUSes.size() > 1) {
							// flag = false;
							System.out.println("index overflow");
						}	
					} 
					catch (ArrayIndexOutOfBoundsException e) {
						flag = false;
						System.out.println("Failed to compute all MUSes.");
					}
				} else {
					System.out.println(ConcateArrayClauses(clauses));
					System.out.println("problem is satisfiable");
					flag = false;
				}
				System.out.println(flag);
				
				if (flag) {	
					System.out.println("flag = true");
					for (IVecInt mus : AllMUSes) {
						int[] indexes = mus.toArray();
						indexes = mainChecker.removeZeroIdxs(indexes);
						row_mus.add(indexes);
					}
					
					if (flag) {
						id += 1;					
						String premise_clause = "";
						
						premise_clause = id + ";" + ConcateArrayClauses(clauses) + ";" + ConcateArrayClauses(row_mus) + ";" + numVars + ";" + numClauses + ";1;" + row_mus.size();
						System.out.println(premise_clause);
						writer.println(premise_clause);
						 
					}
									
				}
				writer.flush();
				
			}
			
			
			writer.close();
			System.out.println("Successfully wrote to the file.");
			System.out.println("VARPOS : " + VARPOS);
			System.out.println("VARNEG : " + VARNEG);
		} catch(IOException e){
			System.out.println("An error occured.");
			e.printStackTrace();
		}
	}

}
