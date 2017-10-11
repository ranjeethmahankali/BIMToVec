from ops import *
import random
random.seed(0.2)

def getAllWords():
    with open('data/vocabulary.dat') as f:
        words = f.read().splitlines()
    wordList = list(words)
    wordDict = dict()
    for i in range(len(words)):
        wordDict[wordList[i]] = i 
    return [wordList, wordDict]

ASCII_DIM = 8
WORD_LEN = 40
WORD_BATCH_SIZE = 20
EMBEDDING_SIZE = 64
EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")

WORDS, WORD_TO_NUM = getAllWords()
TEST_WORDS = random.sample(WORDS, 50)
WORDS = [word for word in WORDS if not word in TEST_WORDS]

VOCAB_SIZE = len(WORDS)

with tf.variable_scope("vars"):
    wc1 = weightVariable([8,8,1,2], 'wc1')
    bc1 = biasVariable([2], 'bc1')

    wc2 = weightVariable([8,8,2,4], 'wc2')
    bc2 = biasVariable([4],'bc2')

    wc3 = weightVariable([8,8,4,6], 'wc3')
    bc3 = biasVariable([6],'bc3')

    wf1 = weightVariable([240, 240],'wf1')
    bf1 = biasVariable([240], 'bf1')

    wf2 = weightVariable([240,64],'wf2')
    bf2 = biasVariable([64],'bf2')

def get_placeholders():
    word_ascii = tf.placeholder(dtype = tf.float32, shape = [None, WORD_LEN, ASCII_DIM, 1])
    embed_true = tf.placeholder(dtype = tf.float32, shape=[None, EMBEDDING_SIZE])
    keep_prob = tf.placeholder(dtype = tf.float32)

    return [word_ascii, embed_true, keep_prob]

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
    # print(word)
    while i < len(word) and len(asciiMat) < WORD_LEN:
        ch = word[i]
        if not ch.isalpha():
            i += 1
            continue
        asciiMat.append(prepareChar(ch))
        i += 1
    
    if len(asciiMat) < WORD_LEN:
        asciiMat += [[0]*ASCII_DIM]*(WORD_LEN - len(asciiMat))
    
    return np.expand_dims(np.array(asciiMat), axis = 2)

def prepWordBatch(words):
    asciiMats = []
    word_embeddings = []
    for word in words:
        mat = prepareWord(word)
        # print(word, mat.shape)
        asciiMats.append(mat)
        word_embeddings.append(EMBEDDINGS[WORD_TO_NUM[word]])
    
    return [np.array(asciiMats), np.array(word_embeddings)]

def reader_model(word_ascii_matrix, keep_prob):
    hc1 = tf.nn.relu(conv2d(word_ascii_matrix, wc1, strides = [1,2,1,1]) + bc1)
    hc2 = tf.nn.relu(conv2d(hc1, wc2, strides = [1,2,1,1]) + bc2)
    hc3 = tf.nn.relu(conv2d(hc2, wc3, strides = [1,2,1,1]) + bc3)

    hf = tf.reshape(hc3, [-1, 240])
    hf1 = tf.nn.relu(tf.matmul(hf, wf1) + bf1)
    hf1_drop = tf.nn.dropout(hf1, keep_prob)
    hf2 = tf.nn.sigmoid(tf.matmul(hf1_drop, wf2) + bf2)

    return hf2

def loss_optim(embed_predict, embed_true):
    losses = tf.reduce_sum(tf.abs(embed_predict - embed_true),axis=0)
    summarize(losses, varName = "embed_losses")
    loss = tf.reduce_mean(losses)

    l2_loss = 0
    all_vars = tf.trainable_variables()
    for v in all_vars:
        l2_loss += alpha * tf.nn.l2_loss(v)
        
    tf.summary.scalar("l2_loss", l2_loss)
    loss += l2_loss
    tf.summary.scalar("total_loss", loss)

    optim = tf.train.AdamOptimizer(learning_rate).minimize(loss)
    return [loss, optim]