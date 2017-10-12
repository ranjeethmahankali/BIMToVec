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
CHAR_LIST = list("abcdefghijklmnopqrstuvwxyz")

WORDS, WORD_TO_NUM = getAllWords()
TEST_WORDS = random.sample(WORDS, 50)
WORDS = [word for word in WORDS if not word in TEST_WORDS]

VOCAB_SIZE = len(WORDS)

LAYER_SIZES = [WORD_LEN, 128, 512, 1024, 1536, 2048, 1536, 1024, 512, 128, 64]

with tf.variable_scope("vars"):
    weights = []
    biases = []

    for i in range(len(LAYER_SIZES)-1):
        weights.append(weightVariable([LAYER_SIZES[i], LAYER_SIZES[i+1]], name = "w%s"%i))
        biases.append(biasVariable([LAYER_SIZES[i+1]], name = "b%s"%i))
        

def get_placeholders():
    word_ascii = tf.placeholder(dtype = tf.float32, shape = [None, WORD_LEN])
    embed_true = tf.placeholder(dtype = tf.float32, shape=[None, EMBEDDING_SIZE])
    keep_prob = tf.placeholder(dtype = tf.float32)

    return [word_ascii, embed_true, keep_prob]

# convert a character to ascii code (8 bits)
def prepareChar(ch):
    return (CHAR_LIST.index(ch)+1)/len(CHAR_LIST)
    # if len(ch) != 1:
    #     raise ValueError("Please supply a single character for the ascii lookup")
    # binStr = "{0:08b}".format(ord(ch))
    # binList = []
    # for d in binStr:
    #     binList.append(int(d))
    
    # return binList

# returns an ascii matrix for word
def prepareWord(word):
    wordArr = []
    i = 0
    # print(word)
    while i < len(word) and len(wordArr) < WORD_LEN:
        ch = word[i]
        if not ch.isalpha():
            i += 1
            continue
        wordArr.append(prepareChar(ch))
        i += 1
    
    if len(wordArr) < WORD_LEN:
        wordArr += [0]*(WORD_LEN - len(wordArr))
    
    # return np.array(wordArr).reshape([1,-1])
    return wordArr

def prepWordBatch(words):
    wordArrs = []
    word_embeddings = []
    for word in words:
        mat = prepareWord(word)
        # print(word, mat.shape)
        wordArrs.append(mat)
        # if wordArrs is None:
        #     wordArrs = mat
        # else:
        #     wordArrs = np.concatenate([wordArrs, mat], axis=0)
        
        word_embeddings.append(EMBEDDINGS[WORD_TO_NUM[word]])
    
    return [np.array(wordArrs), np.array(word_embeddings)]

def reader_model(word_ascii, keep_prob):
    h = None
    for i in range(len(weights)):
        if i == 0:
            h = tf.matmul(word_ascii, weights[i])
        else:
            h = tf.matmul(h, weights[i])
        
        h += biases[i]
        
        if i == len(weights)-1:
            h = tf.nn.tanh(h)
        else:
            h = tf.nn.relu(h)
        
        norm = tf.sqrt(tf.reduce_sum(tf.square(h), 1, keep_dims=True))
        output = h/norm

    return output

def loss_optim(embed_predict, embed_true):
    # losses = tf.reduce_sum(tf.abs(embed_predict - embed_true),axis=0)
    # calculating loss based on dot product
    similarities = tf.diag_part(tf.matmul(embed_predict, tf.transpose(embed_true)))
    summarize(similarities, varName = "similarities")
    loss = 100/tf.reduce_sum(similarities)

    tf.summary.scalar("raw_loss", loss)

    # l2_loss = 0
    # all_vars = tf.trainable_variables()
    # for v in all_vars:
    #     l2_loss += alpha * tf.nn.l2_loss(v)
        
    # tf.summary.scalar("l2_loss", l2_loss)
    # loss += l2_loss
    # tf.summary.scalar("total_loss", loss)

    output_similarity = tf.matmul(embed_predict, tf.transpose(embed_predict))
    summarize(output_similarity, "output_similarity")
    loss += 0.04 * tf.reduce_sum(output_similarity)

    optim = tf.train.AdamOptimizer(learning_rate, beta).minimize(loss)
    # optim = tf.train.GradientDescentOptimizer(0.1).minimize(loss)
    # optim = tf.train.AdagradOptimizer(0.1).minimize(loss)
    # optim = tf.train.ProximalGradientDescentOptimizer(learning_rate).minimize(loss)
    return [loss, optim]