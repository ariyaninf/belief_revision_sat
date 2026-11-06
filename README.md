# Belief Revision Benchmark for Large Reasoning Models

This repository contains the problem generator and the datasets used in the paper:

> **Evaluating Large Reasoning Models on Belief Revision**
> Nurul Fajrin Ariyani, Zied Bouraoui, Richard Booth, Steven Schockaert
> *AACL-IJCNLP 2026 (short paper)*

The benchmark uses **belief revision in propositional logic** to stress-test the reasoning abilities of Large Reasoning Models (LRMs). Although all instances are small (6 atoms, 26 clauses in the main setting), most current models make a significant number of mistakes on them.

---

## Table of Contents

- [Task Definition](#task-definition)
- [Dataset Overview](#dataset-overview)
- [How the Dataset Was Built](#how-the-dataset-was-built)
- [Repository Structure](#repository-structure)
- [Data Format](#data-format)
- [Example Instance](#example-instance)
- [Evaluation Protocol](#evaluation-protocol)
- [Prompts](#prompts)
- [Baseline Results](#baseline-results)
- [Reproducing / Generating New Instances](#reproducing--generating-new-instances)
- [Important Notes](#important-notes)
- [Citation](#citation)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Contact](#contact)

---

## Task Definition

Each problem instance consists of:

- a **knowledge base** `K`: a set of propositional clauses representing initial beliefs, and
- an **observation** `α`: a single clause representing new information.

The model must **add `α` to `K`** and, if `K ∪ {α}` is inconsistent, **remove a minimal set of clauses from `K`** so that the result is consistent again.

Formally, a set `K̂ ⊆ K` is a **valid revision** if:

1. `K̂ ∪ {α}` is satisfiable, and
2. for every `K̃` with `K̂ ⊂ K̃ ⊆ K`, the set `K̃ ∪ {α}` is unsatisfiable (i.e. `K̂` is a *maximal* consistent subset).

Special case: if `K ∪ {α}` is already satisfiable, then `K̂ = K` and **no clause should be removed**.

An instance may have **several valid revisions**; any one of them is accepted as correct.

> **Note on minimality.** Throughout this benchmark, minimality means *subset-minimality*: no strict subset of the removed clauses would suffice. This differs from *cardinality-minimality* (removing the smallest possible number of clauses), which is sometimes used in the belief revision literature.

---

## Dataset Overview

All clauses are 3-literal disjunctions (3-CNF). Unless stated otherwise, each subset contains **100 problem instances**.

| Subset | Description | #Atoms | #Clauses (`\|K ∪ {α}\|`) | Clauses to remove | #Instances |
|---|---|---|---|---|---|
| **Unsatisfiable (main)** | `K ∪ {α}` inconsistent; one clause must be removed | 6 | 26 | 1 | 100 |
| **Satisfiable (main)** | `K ∪ {α}` already consistent; nothing to remove | 6 | 26 | 0 | 100 |
| **Two-clause removal** | Consistency requires removing two clauses | 6 | 26 | 2 | 100 |
| **Varying #clauses** | Scalability with respect to number of clauses | 6 | 29, 32, 35, 38, 41 | 1 | 100 per setting |
| **Varying #atoms** | Scalability with respect to number of atoms | 9, 12 | 26 | 1 | 100 per setting |
| **Entailment** | Derived from the unsatisfiable main set: does `K ⊨ ¬α`? (all positive) | 6 | 26 | – | 100 |
| **Verbalization variants** | Unsatisfiable main set with alternative surface forms (see below) | 6 | 26 | 1 | 100 per variant |

**Verbalization variants**

| Variant | Example for the clause `a ∨ ¬b ∨ c` |
|---|---|
| Default (single subject) | `Alice is smart or Alice is not tall or Alice is helpful.` |
| Multiple subjects | `Alice is smart or Bob is not tall or Carol is helpful.` (each atom refers to a different person) |
| Symbolic | `a or -b or c` |

---

## How the Dataset Was Built

The instances are **synthetically generated**, which allows full control over difficulty and avoids contamination from existing benchmarks.

### Step 1: Sample random 3-CNF formulas

A set of clauses `X` is sampled at random:

- Each clause is a disjunction of **three literals**.
- Each literal is an atom or its negation, **with equal probability**.
- Atoms are drawn from a set `A` with `|A| = 6`.
- Each instance contains **26 clauses**.

The ratio of clauses to atoms (26 / 6 ≈ 4.33) is chosen to approximate the **critical value of ≈ 4.267**, at which randomly generated 3-SAT instances are least likely to be trivially satisfiable or trivially unsatisfiable (Mitchell et al., 1992).

### Step 2: Filter for non-trivial unsatisfiable instances

A sampled set `X` is kept only if it satisfies both criteria:

1. **Single-clause repairability.** `X` is unsatisfiable, but there exist two distinct clauses `α` and `β` in `X` such that both `X \ {α}` and `X \ {β}` are satisfiable.
2. **Multiple conflicts.** `X` has **at least two distinct minimal unsatisfiable subsets** (MUSes).

Criterion 2 ensures that an instance cannot be solved by spotting a single conflict: the model has to find a clause whose removal resolves *all* conflicts at once.

### Step 3: Construct the belief revision problem

From an accepted set `X` with clauses `α` and `β`:

- the knowledge base is `K = X \ {α}` (which is satisfiable),
- the observation is `α`.

Because `X \ {β}` is satisfiable, removing `β` from `K` restores consistency, so the instance is guaranteed to be solvable by removing a **single** clause.

### Step 4: Satisfiable control instances

A separate set of 100 instances `(K, α)` is sampled for which `K ∪ {α}` is **already satisfiable**, using the same parameters (26 clauses in total, 3 literals per clause, 6 atoms). These test whether a model can recognise that **no** revision is needed.

### Step 5: Variants

- **Two-clause removal:** generated with the same procedure, but selecting instances for which restoring consistency requires removing two clauses.
- **Varying clauses / atoms:** same procedure with the number of clauses set to 29–41 (6 atoms), or the number of atoms set to 9 or 12 (26 clauses). Note that moving away from the critical ratio changes the intrinsic difficulty of the instances.
- **Entailment:** for each unsatisfiable instance `(K, α)`, the question is whether `K ⊨ ¬α` (where `¬α` is a conjunction of three literals). Since all instances are taken from the unsatisfiable set, **every entailment instance is positive**.

### Step 6: Verbalization

Symbolic clauses are converted to natural language with the template-based strategy of Ariyani et al. (2025). Each atom is mapped to a phrase `Alice is [adjective]`, negated literals become `Alice is not [adjective]`, and literals are joined with `or`.

### Satisfiability checking

All satisfiability checks during generation and when evaluating model outputs are performed with the **[Sat4J](https://www.sat4j.org/)** solver (Le Berre and Parrain, 2010).

---

## Repository Structure

```
belief_revision_sat/
├── README.md
├── LICENSE
├── generator/                    # Problem generator
│   └── GenerateMUSes.java
│   └── main.java
├── data/
│   ├── main/
│   │   ├── MUS_3satonly_6_fixVars_26_fixCls_100_1.0_500_OR.csv     # 100 unsatisfiable instances (1 removal)
│   │   └── NO_MUS_3satonly_6_fixVars_26_fixCls_100_1.0_500_OR.csv       # 100 satisfiable instances
│   ├── two_removals/
│   │   └── MUS_3satonly_6_fixVars_26_fixCls_100_2.0_500_OR.csv
│   ├── varying_clauses/
│   │   ├── MUS_3sat_6_fixVars_29_fixCls_100_1.0_500_OR.csv
│   │   ├── MUS_3sat_6_fixVars_32_fixCls_100_1.0_500_OR.csv
│   │   └── MUS_3sat_6_fixVars_35_fixCls_100_1.0_500_OR.csv
│   │   └── MUS_3sat_6_fixVars_38_fixCls_100_1.0_500_OR.csv
│   │   └── MUS_3sat_6_fixVars_41_fixCls_100_1.0_500_OR.csv
│   ├── varying_atoms/
│   │   ├── MUS_3sat_9_fixVars_26_fixCls_100_1.0_500_OR.csv
│   │   └── MUS_3sat_12_fixVars_26_fixCls_100_1.0_500_OR.csv
│   ├── entailment/
│   │   └── ENT_3satonly_6_fixVars_26_fixCls_100_1.0_500_OR.csv
│   └── verbalization/
│       ├── MUS_multi_subject_6_fixVars_26_fixCls_100_1.0_500_OR.csv
│       └── MUS_symbolic_6_fixVars_26_fixCls_100_1_0_500_OR.csv
├── prompts/                      # Prompt templates 
│   ├── compact.txt
│   ├── default.txt
│   ├── instruction_driven.txt
│   ├── structured.txt
│   ├── cot_driven.txt
│   ├── entailment.txt
└── evaluation/                   # Scripts for checking model outputs with Sat4J
│   ├── preds_to_dimacs.py        # convert prediction (.json) to dimacs
│   ├── CheckSatisfiability.java
│   ├── main_check.java           # execute the checker
```


### File naming

Dataset files follow the pattern

```
MUS_3satonly_<atoms>_fixVars_<clauses>_fixCls_<instances>_<p1>_<p2>_OR.csv
```

| Part | Example | Meaning |
|---|---|---|
| `MUS` | `MUS` | Instances are annotated with their minimal unsatisfiable subsets |
| `3satonly` | `3satonly` | Every clause has exactly three literals |
| `<atoms>_fixVars` | `6_fixVars` | Number of atoms, fixed for all instances |
| `<clauses>_fixCls` | `26_fixCls` | Number of clauses in `K ∪ {α}`, fixed for all instances |
| `<instances>` | `100` | Number of instances in the file |
| `<p1>` | `1.0` | ⚠️ *to be described* |
| `<p2>` | `500` | ⚠️ *to be described* |
| `OR` | `OR` | ⚠️ *to be described (e.g. clauses verbalized with "or")* |

---

## Data Format

Each dataset is a **semicolon-separated** CSV file (`;`) with a header row. Each row is one problem instance `(K, α)`. The semicolon is used as delimiter because the list-valued columns contain commas.

### Columns

| Column | Format | Description |
|---|---|---|
| `idx` | int | Instance identifier (1–100) |
| `clauses` | `[l, l, l],[l, l, l],...` | All clauses of `X = K ∪ {α}` in symbolic form, **without enclosing brackets**. Atoms are numbered `1..num_atoms`; a positive integer `i` is atom `i`, a negative integer `-i` is its negation (DIMACS style). |
| `mus_idx` | `[i, ...],[i, ...],...` | All minimal unsatisfiable subsets (MUSes) of `X`, each given as a list of **1-based indices into `clauses`**, without enclosing brackets |
| `new_idx` | `[i]` | 1-based index of the observation `α` in `clauses` |
| `nominees_idx` | `[[i], [i], ...]` | Valid single-clause repairs: each inner list is a set of clauses (1-based indices into `clauses`) whose removal from `K` restores consistency |
| `premises` | text | The knowledge base `K` in natural language: all clauses except `α`, in the same order as `clauses`, joined into one string (one sentence per clause, each ending with `.`) |
| `observations` | text | The observation `α` in natural language |
| `nominees` | `[['...'], ['...'], ...]` | The repairs in `nominees_idx`, verbalized (Python list-literal syntax; sentences without the final `.`) |
| `num_atoms` | int | Number of atoms |
| `num_clauses` | int | Number of clauses in `X = K ∪ {α}` |
| `num_muses` | int | Number of MUSes of `X` (= length of `mus_idx`) |

### How the columns relate

- **Indices refer to `clauses`, not to `premises`.** Since `α` is left out of `premises`, the `j`-th premise sentence corresponds to clause `j` if `j < new_idx`, and to clause `j + 1` otherwise.
- Because `K` is satisfiable, **every MUS contains `α`**.
- `nominees_idx` contains exactly the clauses (other than `α`) that occur in **every** MUS. Removing any one of them breaks all conflicts at once, so each is a valid revision.
- `nominees_idx` lists the single-clause repairs only. Subset-minimal repairs that remove two or more clauses (minimal hitting sets of the MUSes) can also exist and are valid answers, so model outputs should be checked with a SAT solver rather than matched against `nominees` (see [Evaluation Protocol](#evaluation-protocol)).
- The atom-to-adjective mapping is **sampled per instance** (the main set uses 359 distinct adjectives). It is not stored as a separate column but can be recovered by aligning `clauses` with the verbalized sentences: literals are verbalized in the same order as in `clauses`.

### Example row (shortened)

```
idx;clauses;mus_idx;new_idx;nominees_idx;premises;observations;nominees;num_atoms;num_clauses;num_muses
1;[-3, -2, 5],[-5, -3, -2],[2, 3, 4],...;[2, 3, 7, 9, 10, 11, 13, 14, 15, 17, 19],...;[2];[[3], [7], [9], [10], [17], [19]];Alice is not fussy or Alice is not blunt or Alice is abnormal. Alice is blunt or Alice is fussy or Alice is orderly. ...;Alice is not abnormal or Alice is not fussy or Alice is not blunt.;[['Alice is blunt or Alice is fussy or Alice is orderly'], ...];6;26;16
```

In this instance, atoms 1–6 are *clever, blunt, fussy, orderly, abnormal, sedate*. The observation is clause 2, `[-5, -3, -2]` (*Alice is not abnormal or Alice is not fussy or Alice is not blunt*). `X` has 16 MUSes, and removing any one of clauses 3, 7, 9, 10, 17 or 19 restores consistency.

### Statistics of the main unsatisfiable set

| | Min | Median | Max |
|---|---|---|---|
| MUSes per instance (`num_muses`) | 2 | 24 | 190 |
| Single-clause repairs per instance (`len(nominees_idx)`) | 1 | 5 | 9 |

### Loading the data

```python
import ast
import re
import pandas as pd


def load_instances(path):
    """Load a belief revision dataset file into a DataFrame with parsed columns."""
    df = pd.read_csv(path, sep=";")
    # Clause lists and MUS lists are stored without enclosing brackets.
    for col in ["clauses", "mus_idx"]:
        df[col] = df[col].apply(lambda s: ast.literal_eval(f"[{s}]"))
    for col in ["new_idx", "nominees_idx", "nominees"]:
        df[col] = df[col].apply(ast.literal_eval)
    # Premises are stored as one string; split it into sentences.
    df["premises"] = df["premises"].apply(lambda s: re.split(r"(?<=\.)\s+", s.strip()))
    return df


df = load_instances("data/MUS_3satonly_6_fixVars_26_fixCls_100_1.0_500_OR.csv")
row = df.iloc[0]

obs = row["new_idx"][0]                                              # 1-based index of α in `clauses`
alpha = row["clauses"][obs - 1]                                      # observation α (symbolic)
K = [c for i, c in enumerate(row["clauses"], start=1) if i != obs]   # knowledge base K (symbolic)

print(alpha, "->", row["observations"])
print(len(K), "clauses in K;", len(row["premises"]), "premise sentences")
```

> **Tip:** opening and re-saving the files in a spreadsheet application (e.g. Excel) can change the delimiter or quoting and break parsing. Use a text editor or the loader above.

---

## Example Instance

An illustrative (shortened) instance, taken from Figure 2 of the paper:

**Knowledge base `K`**
```
1. Alice is not resourceful or Alice is prudent.
2. Alice is not tactless or Alice is not prudent.
3. Alice is not beneficient or Alice is potbellied.
4. Alice is not tactless or Alice is resourceful.
5. Alice is potbellied or Alice is prudent.
6. Alice is not resourceful or Alice is not potbellied.
7. Alice is not prudent or Alice is potbellied.
8. Alice is beneficient or Alice is prudent.
9. Alice is not beneficient or Alice is resourceful.
```

**Observation `α`**
```
10. Alice is beneficient or Alice is resourceful.
```

`K ∪ {α}` is inconsistent. Removing **any one** of clauses 6, 7 or 9 restores consistency, so each of these is a valid answer. Removing more than one of them is **not** minimal.

**Expected output (one valid answer)**
```
removed:   [Alice is not prudent or Alice is potbellied]
remaining: [1, 2, 3, 4, 5, 6, 8, 9, 10]
```

> The real instances in the benchmark contain 26 clauses with three literals each.

---

## Evaluation Protocol

Because multiple valid revisions may exist, answers should **not** be scored by exact match against a single gold answer. Instead, a model's output is verified with a SAT solver:

1. Map the returned clauses back to symbolic form.
2. Check that the observation `α` is included in the final set.
3. Check that the final set is satisfiable.
4. Check that the removal is subset-minimal: adding back any removed clause must make the set unsatisfiable.

An answer is **correct** only if all checks pass. Incorrect answers are categorised as:

| Code | Error type |
|---|---|
| **NM** | *Not minimal*: the result is consistent, but more clauses than necessary were removed |
| **MO** | *Missing observation*: `α` does not appear in the final set |
| **Inc** | *Inconsistent*: the returned set is still unsatisfiable |

An answer can fall under both **MO** and **Inc**, so error counts do not always sum to the number of incorrect answers.

---

## Prompts

The main experiments use the following zero-shot prompt (default prompt, Figure 3 in the paper):

```
Task:
You are an automated belief revision system.
Your goal is to integrate the observations into the premises while
ensuring that the resulting set remains logically consistent.

Instructions:
1. You are given two inputs: Premises and Observations.
2. Check whether Premises ∪ Observations is logically consistent.
3. If Premises ∪ Observations is consistent, output: removed: [],
   remaining: [Premises ∪ Observations].
4. If Premises ∪ Observations is inconsistent, perform belief revision as follows:
   a. Remove the minimal subset of premises such that (Premises − Removed)
      ∪ Observations becomes consistent.
   b. Do not remove observations.
   c. Minimise the number of removed premises, not their content.
5. Your output must be in JSON, exactly in this format:
   {remove: [], remaining: [], justification: explain the reasoning behind your answer.}
6. Do not add new information. Do not modify the original statements.
   Only remove premises when necessary to restore consistency.

[Premises] = [insert a set of beliefs]
[Observations] = [insert observations]
```

Alternative prompts (structured, compact, instruction-driven, chain-of-thought-driven) and the entailment prompt are provided in `prompts/` and described in Appendix C–D of the paper.

---

## Baseline Results

Accuracy (%) on the main sets, default prompt, single run, zero-shot, no tool use:

| Model | Unsatisfiable | Satisfiable |
|---|---|---|
| Grok-4 | **99** | 98 |
| DeepSeek-V3.2 | 91 | 89 |
| Grok-4.3 | 83 | 96 |
| o3 | 81 | **100** |
| Qwen-3 (235B-A22B thinking) | 78 | 98 |
| DeepSeek-R1 | 51 | 79 |
| Gemini-2.5-Pro | 51 | 91 |
| Claude-3.7 (thinking) | 40 | 93 |
| Gemini-2.5-Flash | 33 | 71 |
| o3-mini | 30 | 98 |
| o4-mini | 30 | 94 |
| Olmo-3-32B | 16 | 71 |
| Olmo-3-7B | 4 | 14 |
| Phi-4 (reasoning-plus) | 3 | 7 |
| QWQ-32B | 2 | 88 |

See the paper for confidence intervals, error breakdowns, run-to-run variability, prompt sensitivity and cost analysis.

---

## Reproducing / Generating New Instances

> ⚠️ *Fill in with the actual commands and dependencies.*

```bash
# Requirements: Java (for Sat4J), Python 3.x
git clone https://github.com/ariyaninf/belief_revision_sat.git
cd belief_revision_sat

# Generate 100 unsatisfiable instances with 6 atoms and 26 clauses
python generator/generate.py --atoms 6 --clauses 26 --n 100 --type unsat --out data/new/
```

The generator can be used to create harder instances, for example by increasing the number of clauses or by requiring more clauses to be removed.

---

## Important Notes

- **Intended use.** The dataset is intended for *evaluating* the reasoning abilities of language models. Please **do not include it in training data** for models that will later be evaluated on it.
- **Multiple valid answers.** Always evaluate with a SAT solver rather than string matching against `gold_removed`.
- **Small size.** Each subset has 100 instances to keep the cost of evaluating LRMs manageable. Small differences in accuracy between models should be interpreted with caution.
- **Satisfiable set as control.** Report results on both the unsatisfiable and satisfiable sets: a model that always removes a clause will do well on the former but fail the latter.
- **Entailment set is all-positive.** A trivial model that always answers "Yes" scores 100%; this set is meant as a diagnostic, not a standalone benchmark.
- **Adjective semantics.** Atoms are verbalized with adjectives, but there are no intended commonsense relations between them; only the logical structure matters.

---

## Citation

If you use this dataset or generator, please cite:

```bibtex
@inproceedings{ariyani2026beliefrevision,
  title     = {Evaluating Large Reasoning Models on Belief Revision},
  author    = {Ariyani, Nurul Fajrin and Bouraoui, Zied and Booth, Richard and Schockaert, Steven},
  booktitle = {Proceedings of the 2026 Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics and the International Joint Conference on Natural Language Processing (AACL-IJCNLP)},
  year      = {2026},
  publisher = {Association for Computational Linguistics}
}
```

The verbalization strategy is from:

```bibtex
@inproceedings{ariyani2025simple,
  title     = {There's No Such Thing as Simple Reasoning for {LLM}s},
  author    = {Ariyani, Nurul Fajrin and Bouraoui, Zied and Booth, Richard and Schockaert, Steven},
  booktitle = {Findings of the Association for Computational Linguistics: ACL 2025},
  pages     = {4503--4514},
  year      = {2025},
  address   = {Vienna, Austria},
  publisher = {Association for Computational Linguistics}
}
```

---

## License

> ⚠️ *Choose and add a LICENSE file.* A common choice is **CC BY 4.0** for the data and **MIT** for the code.

---

## Acknowledgments

Nurul Ariyani was supported by Institut Teknologi Sepuluh Nopember (ITS) through the Academic Excellence Research Funding, 3830/PKS/ITS/2026. Steven Schockaert was supported by EPSRC grants EP/W003309/1 and EP/Y028805/1. Zied Bouraoui was supported by ANR-22-CE23-0002 ERIANA.

---

## Contact

- Nurul Fajrin Ariyani — nf.ariyani@its.ac.id
- Steven Schockaert — schockaerts1@cardiff.ac.uk

For questions or issues, please open a GitHub issue.
