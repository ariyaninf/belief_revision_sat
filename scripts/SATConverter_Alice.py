import ast
import random
from copy import deepcopy

import pandas as pd
import numpy as np

df_predicate_list = pd.read_csv('src/vocab_500.txt')


def generate_sentence(atom):
    random_predicate = df_predicate_list.iloc[random.randint(0, len(df_predicate_list) - 1)]['predicates']
    if atom > 0:
        sentence = "Alice is " + random_predicate
    else:
        sentence = "Alice is not " + random_predicate
    return sentence


def flip_sentence(sent, atom):
    words = sent.split()
    if atom > 0:
        sentence = words[0] + " is not " + words[2]
    else:
        sentence = words[0] + " is " + words[3]
    return sentence


def gen_1sat_sentence(formula, df):
    atom = formula
    sent = df.loc[df.atom == atom[0], 'sentence'].values[0]
    return sent, sent


def gen_2sat_sentence(formula, df, temp_type):
    atom_a = formula[0]
    atom_b = formula[1]
    a = df.loc[df.atom == atom_a, 'sentence'].values[0]
    b = df.loc[df.atom == atom_b, 'sentence'].values[0]
    not_a = df.loc[df.atom == -atom_a, 'sentence'].values[0]
    not_b = df.loc[df.atom == -atom_b, 'sentence'].values[0]
    if temp_type == "easy":
        idx = random.randint(1, 6)
    elif temp_type == "hard":
        idx = random.randint(1, 10)
    elif temp_type == "or_only":
        idx = random.randint(1, 2)
    switcher = {
        1: a + " or " + b,
        2: b + " or " + a,
        3: "If " + not_a + " then " + b,
        4: "If " + not_b + " then " + a,
        5: b + " if " + not_a,
        6: a + " if " + not_b,
        7: b + " whenever " + not_a,
        8: b + " provided that " + not_a,
        9: a + " whenever " + not_b,
        10: a + " provided that " + not_b
    }
    sat_sent = a + " or " + b
    return switcher.get(idx, "none"), sat_sent


def gen_3sat_sentence(formula, df, temp_type):
    atom_a = formula[0]
    atom_b = formula[1]
    atom_c = formula[2]
    a = df.loc[df.atom == atom_a, 'sentence'].values[0]
    b = df.loc[df.atom == atom_b, 'sentence'].values[0]
    c = df.loc[df.atom == atom_c, 'sentence'].values[0]
    not_a = df.loc[df.atom == -atom_a, 'sentence'].values[0]
    not_b = df.loc[df.atom == -atom_b, 'sentence'].values[0]
    not_c = df.loc[df.atom == -atom_c, 'sentence'].values[0]
    if temp_type == "easy":
        idx = random.randint(1, 30)
    elif temp_type == "medium":
        idx = random.randint(1, 42)
    elif temp_type == "hard":
        idx = random.randint(1, 78)
    elif temp_type == "or_only":
        idx = random.randint(1, 6)
    switcher = {
        1: a + " or " + b + " or " + c,
        2: a + " or " + c + " or " + b,
        3: b + " or " + a + " or " + c,
        4: b + " or " + c + " or " + a,
        5: c + " or " + a + " or " + b,
        6: c + " or " + b + " or " + a,
        7: "If " + not_a + " and " + not_b + " then " + c,
        8: "If " + not_b + " and " + not_a + " then " + c,
        9: c + " if " + not_a + " and " + not_b,
        10: c + " if " + not_b + " and " + not_a,
        11: "If " + not_c + " then " + a + " or " + b,
        12: "If " + not_c + " then " + b + " or " + a,
        13: a + " or " + b + " if " + not_c,
        14: b + " or " + a + " if " + not_c,
        15: "If " + not_b + " and " + not_c + " then " + a,
        16: "If " + not_c + " and " + not_b + " then " + a,
        17: a + " if " + not_b + " and " + not_c,
        18: a + " if " + not_c + " and " + not_b,
        19: "If " + not_a + " then " + b + " or " + c,
        20: "If " + not_a + " then " + c + " or " + b,
        21: b + " or " + c + " if " + not_a,
        22: c + " or " + b + " if " + not_a,
        23: "If " + not_a + " and " + not_c + " then " + b,
        24: "If " + not_c + " and " + not_a + " then " + b,
        25: b + " if " + not_a + " and " + not_c,
        26: b + " if " + not_c + " and " + not_a,
        27: "If " + not_b + " then " + a + " or " + c,
        28: "If " + not_b + " then " + c + " or " + a,
        29: a + " or " + c + " if " + not_b,
        30: c + " or " + a + " if " + not_b,

        31: "If neither " + a + " nor " + b + " then " + c,
        32: "If neither " + b + " nor " + a + " then " + c,
        33: "If neither " + b + " nor " + c + " then " + a,
        34: "If neither " + c + " nor " + b + " then " + a,
        35: "If neither " + a + " nor " + c + " then " + b,
        36: "If neither " + c + " nor " + a + " then " + b,
        37: c + " if neither " + a + " nor " + b,
        38: c + " if neither " + b + " nor " + a,
        39: a + " if neither " + b + " nor " + c,
        40: a + " if neither " + c + " nor " + b,
        41: b + " if neither " + a + " nor " + c,
        42: b + " if neither " + c + " nor " + a,

        43: c + " whenever " + not_a + " and " + not_b,
        44: c + " whenever " + not_b + " and " + not_a,
        45: c + " whenever neither " + a + " nor " + b,
        46: c + " whenever neither " + b + " nor " + a,
        47: c + " provided that " + not_a + " and " + not_b,
        48: c + " provided that " + not_b + " and " + not_a,
        49: c + " provided that neither " + a + " nor " + b,
        50: c + " provided that neither " + b + " nor " + a,
        51: a + " or " + b + " whenever " + not_c,
        52: b + " or " + a + " whenever " + not_c,
        53: a + " or " + b + " provided that " + not_c,
        54: b + " or " + a + " provided that " + not_c,
        55: a + " whenever " + not_b + " and " + not_c,
        56: a + " whenever " + not_c + " and " + not_b,
        57: a + " whenever neither " + b + " nor " + c,
        58: a + " whenever neither " + b + " nor " + c,
        59: c + " provided that " + not_b + " and " + not_c,
        60: c + " provided that " + not_c + " and " + not_b,
        61: a + " provided that neither " + b + " nor " + c,
        62: a + " provided that neither " + c + " nor " + b,
        63: b + " or " + c + " whenever " + not_a,
        64: c + " or " + b + " whenever " + not_a,
        65: b + " or " + c + " provided that " + not_a,
        66: c + " or " + b + " provided that " + not_a,
        67: b + " whenever " + not_a + " and " + not_c,
        68: b + " whenever " + not_c + " and " + not_a,
        69: b + " whenever neither " + a + " nor " + c,
        70: b + " whenever neither " + c + " nor " + a,
        71: b + " provided that " + not_a + " and " + not_c,
        72: b + " provided that " + not_c + " and " + not_a,
        73: b + " provided that neither " + a + " nor " + c,
        74: b + " provided that neither " + c + " nor " + a,
        75: a + " or " + c + " whenever " + not_b,
        76: c + " or " + a + " whenever " + not_b,
        77: a + " or " + c + " provided that " + not_b,
        78: c + " or " + a + " provided that " + not_b
    }
    sat_sent = a + " or " + b + " or " + c
    return switcher.get(idx, "none"), sat_sent


def gen_4sat_sentence(formula, df):
    atom_a = formula[0]
    atom_b = formula[1]
    atom_c = formula[2]
    atom_d = formula[3]
    a = df.loc[df.atom == atom_a, 'sentence'].values[0]
    b = df.loc[df.atom == atom_b, 'sentence'].values[0]
    c = df.loc[df.atom == atom_c, 'sentence'].values[0]
    d = df.loc[df.atom == atom_d, 'sentence'].values[0]
    not_a = df.loc[df.atom == -atom_a, 'sentence'].values[0]
    not_b = df.loc[df.atom == -atom_b, 'sentence'].values[0]
    not_c = df.loc[df.atom == -atom_c, 'sentence'].values[0]
    not_d = df.loc[df.atom == -atom_d, 'sentence'].values[0]

    sat_sent = a + " or " + b + " or " + c + " or " + d
    sent = sat_sent
    return sent, sat_sent
