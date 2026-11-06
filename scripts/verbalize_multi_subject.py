import argparse
import os.path
from tqdm import tqdm
from scripts.data_preprocessing.LiteralContainer_Names import *
import csv
import pandas as pd
import itertools


def init():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--dataset', default='MUS_3satonly_6_fixVars_26_fixCls_100_1.0', type=str)
    arg_parser.add_argument('--dataset_path', default='dataset/multi_exps/', type=str)
    arg_parser.add_argument('--res_path', default='dataset/multi_exps/', type=str)
    arg_parser.add_argument('--temp_type', default='or_only', type=str)
    arg_parser.add_argument('--vocabs', default='500', type=str)
    args = arg_parser.parse_args()
    return args


def sat_to_sentence(sat, l_cont, temp_type):
    len_sat = len(sat)
    new_sent = ""
    new_basic_sent = ""
    match len_sat:
        case 1:
            new_sent, new_basic_sent = gen_1sat_sentence(sat, l_cont.list_literals)
        case 2:
            new_sent, new_basic_sent = gen_2sat_sentence(sat, l_cont.list_literals, temp_type)
        case 3:
            new_sent, new_basic_sent = gen_3sat_sentence(sat, l_cont.list_literals, temp_type)
        case 4:
            new_sent, new_basic_sent = gen_4sat_sentence(sat, l_cont.list_literals)
    return new_sent, new_basic_sent


def generate_all_premises(set_premises, l_cont, temp_type):
    gen_premises = []
    for pm in set_premises:
        new_sent, new_basic_sent = sat_to_sentence(pm, l_cont, temp_type)
        gen_premises.append(new_basic_sent)

    return gen_premises


def find_min_subset_from_strings(*string_inputs):
    """Find minimal subset that intersects all given lists (in string form)."""
    # Parse all string inputs into tuples of lists
    all_lists = []
    for s in string_inputs:
        parsed = parse_string_to_tuple(s)
        all_lists.extend(parsed)

    # Combine all unique elements
    all_elements = sorted(set(e for lst in all_lists for e in lst))

    # Try subsets in increasing size
    for r in range(1, len(all_elements) + 1):
        for subset in itertools.combinations(all_elements, r):
            # Check if subset "hits" (intersects) all lists
            if all(any(x in lst for x in subset) for lst in all_lists):
                return list(subset)
    return []  # No subset found


def find_all_min_hitting_sets(*string_inputs):
    """Find all minimal hitting sets from string-form inputs."""

    # Parse all string inputs into tuples of lists
    all_lists = []
    remove = 0
    for s in string_inputs:
        parsed = parse_string_to_tuple(s)
        all_lists.extend(parsed)

    # Combine all unique elements
    all_elements = sorted(set(e for lst in all_lists for e in lst))

    all_min_sets = []
    found_min_size = None

    # Try subsets in increasing size
    for r in range(1, len(all_elements) + 1):
        current_sets = []
        remove = 0
        for subset in itertools.combinations(all_elements, r):
            # Check if subset "hits" (intersects) all lists
            if all(any(x in lst for x in subset) for lst in all_lists):
                remove = len(subset)
                current_sets.append(subset)

        if current_sets:  # Found hitting sets of size r
            found_min_size = r
            all_min_sets = current_sets
            break  # Stop — we only want *minimal* ones

    # Convert tuples to lists for cleaner output
    return [list(s) for s in all_min_sets], remove


def parse_string_to_tuple(s):
    """Safely parse string into a tuple of lists."""
    s = s.strip()
    # Wrap in parentheses if not already a tuple
    if not s.startswith("("):
        s = f"({s})"
    value = ast.literal_eval(s)
    # Ensure consistent tuple format
    if isinstance(value, list):
        return (value,)
    return value


def remove_atoms(lists, atoms):
    atoms_set = set(atoms)  # faster lookup
    return [[x for x in lst if x not in atoms_set] for lst in lists]


if __name__ == '__main__':
    args = init()

    f_name = args.dataset + ".csv"
    f_main = os.path.join(args.dataset_path, f_name)
    # args.dataset = args.dataset[:-9]
    f_res_main = ""

    if args.temp_type == 'easy':
        f_res_main = os.path.join(args.res_path, args.dataset + "_" + args.vocabs + "_ER.csv")
    elif args.temp_type == 'medium':
        f_res_main = os.path.join(args.res_path, args.dataset + "_" + args.vocabs + "_MR.csv")
    elif args.temp_type == 'hard':
        f_res_main = os.path.join(args.res_path, args.dataset + "_" + args.vocabs + "_HR.csv")
    elif args.temp_type == "or_only":
        f_res_main = os.path.join(args.res_path, args.dataset + "_" + args.vocabs + "_OR.csv")

    if os.path.exists(f_res_main):
        print("File is already exists.")

    csv.field_size_limit(100000000)

    df_main = pd.read_csv(f_main, sep=';', engine='python')

    # fmain = open(f_res_main, "a+")

    with open(f_res_main, 'w') as file_main:
        file_main.write(
            "idx;clauses;new_idx;nominees_idx;num_remove;"
            "premises;observations;nominees;num_atoms;num_clauses;num_muses\n")

        for row in tqdm(df_main.values):

            idx = row[0]
            mus_idx = row[2]
            num_atoms = row[3]
            num_clauses = row[4]
            mus_set = row[6]

            ''' --- 1. Translate premises, LC initiation, (sentence1) --- '''
            prem_str = row[1]
            lc = LiteralContainer(prem_str)
            premises = ast.literal_eval(prem_str)

            if isinstance(premises, list):
                row[1] = row[1] + ','
                premises = ast.literal_eval(row[1])

            list_premises = generate_all_premises(premises, lc, args.temp_type)

            ''' --- 2. Find and translate new_clauses indexes. Remove new_clauses from main_sent --- '''
            muses = ast.literal_eval(mus_idx)
            if isinstance(muses, list):
                row[2] = row[2] + ","
                muses = ast.literal_eval(row[2])

            new_idx = find_min_subset_from_strings(mus_idx)
            new_muses = remove_atoms(muses, new_idx)

            sent_new_cls = ""
            main_sent = ""
            all_sent = ""

            for i in range(len(list_premises)):
                if i + 1 not in new_idx:
                    main_sent += list_premises[i] + ". "
                else:
                    sent_new_cls += list_premises[i] + ". "
                all_sent += list_premises[i] + ". "

            sent_new_cls = sent_new_cls[:-1]
            main_sent = main_sent[:-1]
            all_sent = all_sent[:-1]

            ''' --- 3. List nominees --- '''
            new_muses = str(new_muses)
            str_new_muses = new_muses[1:-1]
            nominees_idx, num_remove = find_all_min_hitting_sets(str_new_muses)
            nominees_idx = str(nominees_idx)

            sent_nominees = []

            nominee_list = ast.literal_eval(nominees_idx[1:-1])
            if isinstance(nominee_list, list):
                nominees_idx = nominees_idx[1:-1] + ","
                nominee_list = ast.literal_eval(nominees_idx)

            for nom in nominee_list:
                str_nominees = []
                for i in nom:
                    str_nominees.append(list_premises[i-1])
                sent_nominees.append(str_nominees)

            ''' --- 6. Concatenate sentences as a row --- '''
            # idx;clauses;mus_idx;new_idx;nominees_idx;premises;observations;nominees;num_atoms;num_clauses;num_muses
            sent_row = str(idx) + ";" + \
                       prem_str + ";" + \
                       str(new_idx) + ";" + \
                       str(nominees_idx) + ";" + \
                       str(num_remove) + ";" + \
                       main_sent + ";" + \
                       sent_new_cls + ";" + \
                       str(sent_nominees) + ";" + \
                       str(num_atoms) + ";" + \
                       str(num_clauses) + ";" + \
                       str(mus_set) + "\n"
            file_main.write(sent_row)

        file_main.close()
        print("Successfully wrote all entailment pairs.")



