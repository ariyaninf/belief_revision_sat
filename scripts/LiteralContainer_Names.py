from scripts.data_preprocessing.SATConverter_Names import *
import ast


class LiteralContainer:
    list_literals = pd.DataFrame(columns=['atom', 'sentence'])

    def __init__(self, formulas):
        clauses = ast.literal_eval(formulas)
        for clause in clauses:
            self.add_clause(clause)

    def add_new_literal(self, new_atom):
        sentence = ''
        if new_atom not in self.list_literals.values:
            while not sentence or sentence in self.list_literals['sentence'].values:
                sentence = generate_sentence(new_atom)

            self.list_literals = pd.concat([self.list_literals, pd.DataFrame.from_records([{
                'atom': new_atom, 'sentence': sentence
            }])])
            self.list_literals = pd.concat([self.list_literals, pd.DataFrame.from_records([{
                'atom': -new_atom, 'sentence': flip_sentence(sentence, new_atom)
            }])])
            self.list_literals = self.list_literals.reset_index(drop=True)

    def add_clause(self, clause):
        gen_sent = ''
        if isinstance(clause, int):
            clause = [int(clause)]
        for cl in clause:
            if cl not in self.list_literals.values:
                while not gen_sent or gen_sent in self.list_literals['sentence'].values:
                    gen_sent = generate_sentence(cl)

                self.list_literals = pd.concat([self.list_literals, pd.DataFrame.from_records([{
                    'atom': cl, 'sentence': gen_sent
                }])])
                self.list_literals = pd.concat([self.list_literals, pd.DataFrame.from_records([{
                    'atom': -cl, 'sentence': flip_sentence(gen_sent, cl)
                }])])
                self.list_literals = self.list_literals.reset_index(drop=True)

    def add_entailment(self, hypo):
        gen_sent = ''
        atom_list = ast.literal_eval(hypo)
        for h in atom_list:
            if h not in self.list_literals.values:
                while not gen_sent or gen_sent in self.list_literals['sentence'].values:
                    gen_sent = generate_sentence(h)

                self.list_literals = pd.concat([self.list_literals, pd.DataFrame.from_records([{
                    'atom': h, 'sentence': gen_sent
                }])])
                self.list_literals = pd.concat([self.list_literals, pd.DataFrame.from_records([{
                    'atom': -h, 'sentence': flip_sentence(gen_sent, h)
                }])])
                self.list_literals = self.list_literals.reset_index(drop=True)
