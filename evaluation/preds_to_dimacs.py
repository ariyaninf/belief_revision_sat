import json
import os
from tqdm import tqdm
import pandas as pd
import re


dataset_path = "" # insert the dataset path where you store the prediction json file
file_name = ""  # insert the file name of prediction
file_gold_label = "" # insert the dataset file name in "data/..."


def parse_input(str_remaining):
    # Initialize a shared dictionary for both inputs
    literal_to_number = {}
    number_to_literal = {}
    literal_count = 1

    # Helper function to process a single input string into DIMACS clauses
    def process_string(input_string):
        nonlocal literal_count
        sentences = input_string
        dimacs_clauses = []

        for sentence in sentences:
            parts = sentence.split(' or ')
            clause = []

            for part in parts:
                part = part.strip()
                part = part.replace('.', '')
                if part != "":
                    if part.startswith('Alice is '):
                        literal = part[9:]  # Remove "Alice is "
                    elif part.startswith('Alice '):
                        literal = part[6:]  # Remove "Alice "

                    # Assign numeric codes
                    if literal not in literal_to_number:
                        if 'not ' in literal:
                            pos_literal = literal[4:]  # Get the positive literal by removing 'not '
                            neg_literal = literal
                            literal_to_number[pos_literal] = literal_count
                            literal_to_number[neg_literal] = -literal_count
                            number_to_literal[literal_count] = pos_literal
                            number_to_literal[-literal_count] = neg_literal
                        else:
                            pos_literal = literal
                            literal_to_number[pos_literal] = literal_count
                            neg_literal = 'not ' + literal
                            literal_to_number[neg_literal] = -literal_count
                            number_to_literal[literal_count] = pos_literal
                            number_to_literal[-literal_count] = neg_literal
                        literal_count += 1

                    clause.append(literal_to_number[literal])

            if clause:
                dimacs_clauses.append(clause)

        return dimacs_clauses

    # Process both input strings
    rem_dmcs = process_string(str_remaining)

    return rem_dmcs


def dimacs_format(dimacs_clauses):
    all_clauses = (c for c in dimacs_clauses if c)
    dimacs = ','.join(str(clause) for clause in all_clauses)
    return dimacs


def load_nominees(file_gold_label):
    df = pd.read_csv(file_gold_label, sep=';')
    nominees_dict = {}

    for _, row in df.iterrows():
        idx = row['id'] if 'id' in df.columns else row['idx']
        nominees_raw = row['nominees']
        try:
            # Convert string representation to Python list
            nominees = eval(nominees_raw)
        except Exception:
            nominees = []
        nominees_dict[idx] = nominees
    return nominees_dict


def load_num_muses(file_gold_label):
    df = pd.read_csv(file_gold_label, sep=';')
    num_muses_dict = {}

    for _, row in df.iterrows():
        idx = row['id'] if 'id' in df.columns else row['idx']
        num_muses = row['num_muses']
        num_muses_dict[idx] = num_muses
    return num_muses_dict


def load_observers(f_gold_label):
    df = pd.read_csv(f_gold_label, sep=';')
    obs_dict = {}

    for _, row in df.iterrows():
        idx = row['id'] if 'id' in df.columns else row['idx']
        observations = row['observations']
        obs_dict[idx] = observations
    return obs_dict


def clean_sentences(sent_list):
    """Remove trailing periods and extra spaces from each sentence."""
    return [s.strip().rstrip('.').strip() for s in sent_list]


def is_minimal(idx, removed, nominees_dict):
    """
    Compare removed with nominees for a given idx.
    Returns 1 if removed matches any nominee set (ignoring order), else 0.
    """
    if idx not in nominees_dict:
        return 0

    # Clean sentences (remove trailing '.')
    removed_clean = clean_sentences(removed)
    set_removed = set(removed_clean)

    nominees = nominees_dict[idx]

    print("idx:", idx)

    for nominee in nominees:
        nominee_clean = clean_sentences(nominee)
        set_nominee = set(nominee_clean)
        if set_removed == set_nominee:
            return 1
    return 0


def is_subset(list_a, list_b):
    """Checks if all elements in list_a are present in list_b."""
    # Convert list_b to a set for O(1) average time complexity lookups
    b_set = set(list_b)
    # Check if every element of list_a is present in the set b_set
    return all(item in b_set for item in list_a)


def is_obs_exists(observers, remaining):
    count = 0
    observers = [p.strip() for p in observers.split('. ') if p.strip()]
    list_observers = [p if p.endswith('.') else p + '.' for p in observers]

    print("observers: ", list_observers)
    print("remaining: ", remaining)

    if is_subset(list_observers, remaining):
        return 1
    else:
        return 0


def main():
    f_main = os.path.join(dataset_path, file_name + ".json")
    print(f_main)

    with open(f_main, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    print(f"Loaded {len(data)} entries")

    # Output directory
    # directory = os.path.join(dataset_path, "dimacs")
    # os.makedirs(directory, exist_ok=True)

    # Load gold label nominees
    nominees_dict = load_nominees(file_gold_label)
    num_muses_dict = load_num_muses(file_gold_label)
    obs_dict = load_observers(file_gold_label)
    print(f"Loaded nominees for {len(nominees_dict)} items from gold label")

    f_res_main = os.path.join(dataset_path, "dimacs_" + file_name + ".csv")

    with open(f_res_main, "w", encoding="utf-8") as file_wrt:
        file_wrt.write("idx;observations;remaining_sent;remaining;removed;nominees;num_atoms;num_clauses;num_muses;"
                       "prompt_tokens;output_tokens;minimal;obs_in_rem;no_rem\n")

        for entry in tqdm(data):
            idx = entry.get("id", 0)
            remaining = entry.get("remaining", [])
            removed = entry.get("removed", [])
            nominees = nominees_dict[idx]
            num_atoms = entry.get("num_atoms", 0)
            num_clauses = entry.get("num_clauses", 0)
            num_muses = num_muses_dict[idx]
            prompt_tokens = entry.get("prompt_tokens", 0)
            output_tokens = entry.get("output_tokens", 0)
            observations = obs_dict[idx]

            # Compute minimality
            minimal_val = is_minimal(idx, removed, nominees_dict)
            obs_in_rem = is_obs_exists(observations, remaining)
            if not removed:
                no_rem = 1
            else:
                no_rem = 0

            dimacs_remaining = parse_input(remaining)
            sent_row = f"{idx};{observations};{remaining};{dimacs_remaining};{removed};{nominees};{num_atoms};{num_clauses};{num_muses};" \
                       f"{prompt_tokens};{output_tokens};{minimal_val};{obs_in_rem};{no_rem}\n"
            file_wrt.write(sent_row)

    print(f"Succesfully wrote all entailment pairs to {f_res_main}")


if __name__ == "__main__":
    main()
