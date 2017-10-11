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
    w1 = weightVariable([ASCII_DIM*WORD_LEN, 480], 'w1')
    b1 = biasVariable([480], 'b1')

    w2 = weightVariable([480, 640], 'w2')
    b2 = biasVariable([640],'b2')

    w3 = weightVariable([640, 1024], 'w3')
    b3 = biasVariable([1024],'b3')

    w4 = weightVariable([1024, 640],'w4')
    b4 = biasVariable([640], 'b4')

    w5 = weightVariable([640, 320], 'w5')
    b5 = biasVariable([320], 'b5')

    w6 = weightVariable([320, 64], 'w6')
    b6 = biasVariable([64],'b6')
    

def get_placeholders():
    word_ascii = tf.placeholder(dtype = tf.float32, shape = [None, WORD_LEN*ASCII_DIM])
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
    
    return np.array(asciiMat).reshape([1,-1])

def prepWordBatch(words):
    asciiMats = None
    word_embeddings = []
    for word in words:
        mat = prepareWord(word)
        # print(word, mat.shape)
        if asciiMats is None:
            asciiMats = mat
        else:
            asciiMats = np.concatenate([asciiMats, mat], axis=0)
        
        word_embeddings.append(EMBEDDINGS[WORD_TO_NUM[word]])
    
    return [asciiMats, np.array(word_embeddings)]

def reader_model(word_ascii, keep_prob):
    h1 = tf.nn.relu(tf.matmul(word_ascii, w1) + b1)
    h2 = tf.nn.relu(tf.matmul(h1, w2) + b2)
    h3 = tf.nn.relu(tf.matmul(h2, w3) + b3)
    h4 = tf.nn.relu(tf.matmul(h3, w4) + b4)

    h4_drop = tf.nn.dropout(h4, keep_prob)
    h5 = tf.nn.relu(tf.matmul(h4_drop, w5) + b5)
    h6 = tf.nn.tanh(tf.matmul(h5, w6) + b6)

    return (1+h6)/2

def loss_optim(embed_predict, embed_true):
    # losses = tf.reduce_sum(tf.abs(embed_predict - embed_true),axis=0)
    # calculating loss based on dot product
    losses = tf.diag_part(tf.matmul(embed_predict, tf.transpose(embed_true)))
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