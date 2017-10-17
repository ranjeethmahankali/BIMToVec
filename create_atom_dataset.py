from ops import *

ATOMS, atomToNum = getAllAtoms()
WORDS, WORD_TO_NUM = getAllWords()

# loading the dataset
words_dataset = dataset("data/")
def export_atom_dataset():
    pairs = []
    for word in WORDS:
        pool = []
        for atom in ATOMS:
            if atom in word:
                pool.append(atom)

        if len(pool) == 0:
            continue

        for i in range(len(pool)):
            for j in range(i+1, len(pool)):
                pairs.append([ATOMS.index(pool[i]), ATOMS.index(pool[j])])

    return pairs

def write_pairs_to_file(pairs, path):
    with open(path,"w") as f:
        for pair in pairs:
            f.write("%s %s\n"%(pair[0], pair[1]))

if __name__ == "__main__":
    pairs = export_atom_dataset()
    write_pairs_to_file(pairs, "data/atoms/atom_dataset.dat")