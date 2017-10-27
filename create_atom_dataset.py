from ops import *

ATOMS, atomToNum = getAllAtoms()
WORDS, WORD_TO_NUM = getAllWords()
DATA_COUNT = 0
MAX_PER_FILE = 6000000
FILE_NUM = 0

def get_file_path(num):
    return "data/atoms/atom_dataset_%s.dat"%num

F = open(get_file_path(FILE_NUM), "w")

def export_pair(pair):
    global DATA_COUNT, MAX_PER_FILE, FILE_NUM, F
    F.write("%s %s\n" % (pair[0], pair[1]))
    DATA_COUNT += 1
    if DATA_COUNT >= MAX_PER_FILE:
        FILE_NUM += 1
        DATA_COUNT = 0

        F.close()
        F = open(get_file_path(FILE_NUM), "w")


# loading the dataset
def export_atom_dataset():
    for word in WORDS:
        pool = []
        for atom in ATOMS:
            if atom in word:
                pool.append(atom)

        if len(pool) < 1:
            continue

        for w1 in pool:
            for w2 in pool:
                if w1 == w2:
                    continue
                export_pair([ATOMS.index(w1), ATOMS.index(w2)])

if __name__ == "__main__":
    export_atom_dataset()
    F.close()