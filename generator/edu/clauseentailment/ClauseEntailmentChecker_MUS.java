package edu.clauseentailment;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

import org.sat4j.core.VecInt;
import org.sat4j.minisat.SolverFactory;
import org.sat4j.specs.ContradictionException;
import org.sat4j.specs.ISolver;
import org.sat4j.specs.IVecInt;
import org.sat4j.specs.TimeoutException;
import org.sat4j.tools.*;

public class ClauseEntailmentChecker_MUS {
	private final AllMUSes musFinder;
	private final ISolver solver;	
	
	public ClauseEntailmentChecker_MUS(final int nVars) {
		this.musFinder = new AllMUSes(SolverFactory.instance());
		this.solver = musFinder.getSolverInstance();
		this.solver.newVar(nVars);
		this.solver.setTimeout(Integer.MAX_VALUE);
	}
	
	public void addClause(final int[] dimacsLiterals) throws ContradictionException{
		this.solver.addClause(new VecInt(dimacsLiterals));
	}
	
	public boolean isSatisfiable() {
		try {
			return this.solver.isSatisfiable();
		} catch (TimeoutException e) {
			throw new IllegalStateException("no timeout should occur.");
		}
	}
	
	public boolean isSatisfiable(final int[] clause) {
		try {
			return this.solver.isSatisfiable(new VecInt(clause));
		} catch (TimeoutException e) {
			throw new IllegalStateException("no timeout should occur.");
		}
	}
	
	public boolean isEntailed(final int[] clause) {
		final int[] negClause = Arrays.stream(clause).map(i -> -i).toArray();
		try {
			return !this.solver.isSatisfiable(new VecInt(negClause));
		} catch (TimeoutException e){
			throw new IllegalStateException("no timeout should occur.");
		}
	}
	
	public List<IVecInt> getListMUS(){		
		return this.musFinder.computeAllMUSes();
	}
	
	public String ConcateArrayClauses (List<int[]> cls) {
		String concat = new String();
		for (int[] c : cls) {
			concat = concat + Arrays.toString(c) + ",";
		}
		return concat.substring(0, concat.length() - 1);
	}
	
	public boolean isSatAfterRemoval(List<int[]> clauses, int[] mus_clause) {
		ISolver mus_solver = SolverFactory.newDefault();
		
		List<int[]> temp_clauses = new ArrayList<int[]>(clauses);
		temp_clauses.remove(mus_clause);
		boolean result = true;
		
		// System.out.println("temp_clauses: " + ConcateArrayClauses(temp_clauses));
		
		for (int[] clause : temp_clauses) {
			try {
				mus_solver.addClause(new VecInt(clause));
			} catch (ContradictionException e) {
				result = false;
			}
		}
		
		if (result) {
			try {
				result = mus_solver.isSatisfiable();
			} catch(TimeoutException e) {
				result = false;
			}
		}
		return result;
	}
	
	public List<int[]> getAllMUSClauses(int[] mus_indices, List<int[]> clauses){
		List<int[]> result = new ArrayList<int[]>();
		for (int index : mus_indices) {
			if(index > 0) {
				result.add(clauses.get(index - 1));
			}
		}
		return result;
	}
	
	public int[] removeZeroIdxs(int[] mus_indices) {
		List<Integer> list_result = new ArrayList<Integer>();
		for (int m : mus_indices) {
			if (m > 0) {
				list_result.add(m);
			}
		}
		int[] arr_result = list_result.stream().mapToInt(i->i).toArray();
		return arr_result;
	}
	
	public int most_frequent(List<Integer> list) {
		Map<Object, Long> counts = list.stream().collect(Collectors.groupingBy(e -> e, Collectors.counting()));
		System.out.println("list");
		System.out.println(list);
		System.out.println("counts");
		System.out.println(counts);
		int element = (int) Collections.max(counts.entrySet(), Map.Entry.comparingByValue()).getKey();
		return element;
	}
	
	public List<Integer> GetIndexForRemoval(List<int[]> muses) {
		List<Integer> return_set = new ArrayList<Integer>();
		while (muses.size() > 0) {
			List<Integer> elements = new ArrayList<Integer>();
			for (int[] mus : muses) {
				for (int el : mus) {
					elements.add(el);
				}
			}
			int element = most_frequent(elements);
			return_set.add(element);
			List<int[]> new_set_muses = new ArrayList<int[]>();
			for (int[] m : muses) {
				boolean contains = IntStream.of(m).anyMatch(x -> x == element);		
				if (!contains) {
					new_set_muses.add(m);
				}
			}
			muses = new_set_muses;
		}
		return return_set;
	}

}
