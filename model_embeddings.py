from ops import *

def getAllWrods():
    with open('data/wordList.pkl','rb') as f:
        words = pickle.load(f)
    return words

WORDS = getAllWrods()
VOCAB_SIZE = len(WORDS)
EMBEDDING_SIZE = 64

# Variables
with tf.variable_scope("vars"):
    embeddings = tf.Variable(
        tf.random_uniform([VOCAB_SIZE, EMBEDDING_SIZE], -1.0, 1.0),
        name='embeddings'
    )

    softmax_weights = tf.Variable(
        tf.truncated_normal([VOCAB_SIZE, EMBEDDING_SIZE], stddev=1.0/math.sqrt(EMBEDDING_SIZE)),
        name="weights"
    )

    softmax_biases = tf.Variable(
        tf.zeros([VOCAB_SIZE]),
        name = "biases"
    )

# Model
