from embeddingCalc import *

EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
WORDS, WORD_TO_NUM = getAllWords()

# convert a character to ascii code (8 bits)
def prepareChar(ch):
    if len(ch) != 1:
        raise ValueError("Please supply a single character for the ascii lookup")
    binStr = "{0:08b}".format(ord(ch))
    binList = []
    for d in binStr:
        binList.append(int(d))
    
    return binList

# converts a word into an ascii matrix and ignores non alphabets
def prepareWord(word):
    asciiList = []
    for ch in word:
        if not ch.isalpha():
            continue
        asciiList.append(prepareChar(ch))
    
    return np.array(asciiList)

# converts a list of words to a list of their corresponding ascii matrices
def prepareWordList(words):
    word_matrix = []
    for word in words:
        word_matrix.append(prepareWord(word))
    
    return word_matrix

COUNTER = 0
def next_batch(num):
    word_ascii_matrices = []
    word_embeddings = []
    words = None
    newPos = (COUNTER+num)%len(WORDS)
    if newPos >= COUNTER:
        words = WORDS[COUNTER:newPos]
    else:
        words = WORDS[COUNTER:]
        words += WORDS[0:newPos]

    word_ascii_matrices += prepareWordList(words)
    for word in words:
        word_embeddings.append(toEmbedding(word))

    return [word_ascii_matrices, word_embeddings]

