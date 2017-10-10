from ops import *
from model_embeddings import getAllWords

ASCII_DIM = 8
WORD_LEN = 40
WORD_BATCH_SIZE = 20
EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
WORDS, WORD_TO_NUM = getAllWords()

with tf.variable_scope("vars"):
    wc1 = weight_variable([8,8,1,8], 'wc1')
    bc1 = bias_variable([16])

    wc1 = weight_variable([8,8,16,12], 'wc1')
    bc1 = bias_variable([16])

    wc1 = weight_variable([8,8,1,16], 'wc1')
    bc1 = bias_variable([16])

    # incomplete

def get_placeholders():
    word_ascii = tf.placeholder(dtype = tf.float32, shape = [None, WORD_LEN, ASCII_DIM, 1])
    keep_prob = tf.placeholder(dtype = tf.float32)

# convert a character to ascii code (8 bits)
def prepareChar(ch):
    if len(ch) != 1:
        raise ValueError("Please supply a single character for the ascii lookup")
    binStr = "{0:08b}".format(ord(ch))
    binList = []
    for d in binStr:
        binList.append(int(d))
    
    return binList

# returns an ascii matrix for word
def prepareWord(word):
    asciiMat = []
    i = 0
    while i < len(word) and len(asciiMat) <= WORD_LEN:
        ch = word[i]
        if not ch.isalpha():
            continue
        asciiMat.append(prepareChar(ch))
        i += 1
    
    if len(asciiMat) < WORD_LEN:
        asciiMat += [[0]*ASCII_DIM]*(WORD_LEN - len(ascii))
    
    return np.expand_dims(np.array(asciiMat), axis = 2)

def prepWordBatch(words):
    asciiMats = []
    word_embeddings = []
    for word in words:
        asciiMats.append(prepareWord(word))
        word_embeddings.append(EMBEDDINGS[WORD_TO_NUM[word]])
    
    return [np.array(asciiMats), np.array(word_embeddings)]

def get_embeddings(words):

