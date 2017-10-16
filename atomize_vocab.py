from ops import *
from collections import *
import multiprocessing as mp
import spacy
nlp = spacy.load("en")

WORDS, WORD_TO_NUM = getAllWords()
MIN_WORD_LENGTH = 2
MIN_COUNT = 2
WORD_COUNT = len(WORDS)

def longest_common_substring(s1, s2):
    mat = np.zeros([len(s1), len(s2)], np.int32)
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                base = 0 if (i < 1 or j < 1) else mat[i-1, j-1]
                mat[i,j] = base + 1

    maxPos = np.unravel_index(mat.argmax(),mat.shape)
    maxVal = mat[maxPos[0], maxPos[1]]
    substr = None
    if maxPos[0]+1 >= len(s1):
        substr = s1[maxPos[0]-maxVal+1:]
    else:
        substr = s1[maxPos[0]-maxVal+1: maxPos[0]+1]

    return substr

def atomize_vocabulary(vocab, passes = 1):
    BASE_VOCAB = set()
    for word in vocab:
        BASE_VOCAB.update(atomize_word(word, vocab))
        # vocab.remove(word)
    return BASE_VOCAB

# This function computes and returns the LevenshteinDistance between two strings
def LevenshteinDistance(s, t):
    if s == "":
        return len(t)
    if t == "":
        return len(s)
    if s[-1] == t[-1]:
        cost = 0
    else:
        cost = 1

    res = min([LevenshteinDistance(s[:-1], t) + 1,
               LevenshteinDistance(s, t[:-1]) + 1,
               LevenshteinDistance(s[:-1], t[:-1]) + cost])
    return res

def remove_similar(wordSet, score_dict):
    for w1 in wordSet:
        for w2 in wordSet:
            if w1 == w2:
                continue

            LD = LevenshteinDistance(w1, w2)
            MIN_LEVENSHTEIN = min(min(len(w1), len(w2))//2, 3)

            if LD <= MIN_LEVENSHTEIN:
                if score_dict[w1] > score_dict[w2]:
                    wordSet.remove(w2)
                elif score_dict[w1] < score_dict[w2]:
                    wordSet.remove(w1)

    return wordSet

def atomize_word(word, vocab):
    ATOMIZED = defaultdict(int)
    for w in vocab:
        if w == word:
            continue
        substr = longest_common_substring(w, word)
        if len(substr) > 2:# and substr in nlp.vocab:
            ATOMIZED[substr] += 1

    SCORE_DICT = {word: score_word(word, ATOMIZED[word]) for word in ATOMIZED}
    SORTED = sorted(ATOMIZED, key=lambda x: SCORE_DICT[x], reverse=True)
    WORD_LIST = [w for w in SORTED if ATOMIZED[w] > MIN_COUNT]
    WORD_LIST = remove_similar(WORD_LIST, SCORE_DICT)

    scores = np.array([SCORE_DICT[w] for w in WORD_LIST])
    mean = scores.mean()
    std = scores.std()
    limit = mean + (0.05 * std)

    ATOMS = []
    for i in range(len(WORD_LIST)):
        if i <= (len(WORD_LIST)//5)+1 or scores[i] >= limit:
            ATOMS.append(WORD_LIST[i])

    return ATOMS


def score_word(word, count):
    effectiveLength = min(len(word)-MIN_WORD_LENGTH, 10)
    base = 3 if (len(word) > MIN_WORD_LENGTH +1 and word in nlp.vocab) else 1.5
    score = count*(base**effectiveLength)
    return score

atom_vocab_file = open("data/atom_vocabulary.dat", "w")

GLOBAL_COUNT = 0
GLOBAL_ATOMS = set()
def print_atoms(word):
    global GLOBAL_COUNT
    atoms = atomize_word(word, WORDS)
    GLOBAL_COUNT += 1
    print("[%s of %s] - %s: %s" % (GLOBAL_COUNT, WORD_COUNT,word, ", ".join(atoms)))
    for atom in atoms:
        atom_vocab_file.write(atom+"\n")


if __name__ == "__main__":
    pool = mp.Pool(processes=2)
    pool.map(print_atoms, WORDS)