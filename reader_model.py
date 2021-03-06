from ops import *
import math
import random

ATOM_NUM = 5
ATOM_SIZE = 32
WORD_SIZE = 64
WORD_SAMPLE_SIZE = 20

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
EMBEDDING_TENSOR = tf.constant(value=EMBEDDINGS, dtype=tf.float32)

def get_char_list_vec(word):
    chars = ""
    if len(word) < WORD_SAMPLE_SIZE:
        while len(chars) < WORD_SAMPLE_SIZE:
            chars += word
        if len(chars) > WORD_SAMPLE_SIZE:
            chars = chars[:WORD_SAMPLE_SIZE]
            # print(chars)
    else:
        chars = random.sample(list(word), WORD_SAMPLE_SIZE)

    vec = []
    for ch in chars:
        vec += [(ALPHABET.index(ch)+1)/len(ALPHABET)]

    return np.reshape(np.array(vec),[1,-1])

LAYERS = [(ATOM_NUM*ATOM_SIZE)+WORD_SAMPLE_SIZE, 640, 1280, 1536, 1280, 640, WORD_SIZE]

with tf.variable_scope("vars"):
    weights = [
        weightVariable([LAYERS[i], LAYERS[i+1]], name="w%s"%i) for i in range(len(LAYERS)-1)
    ]

    biases = [
        biasVariable([LAYERS[i+1]], name="b%s"%i) for i in range(len(LAYERS)-1)
    ]

atoms_placeholder = tf.placeholder(shape=[None, (ATOM_NUM*ATOM_SIZE)+WORD_SAMPLE_SIZE],
                       dtype = tf.float32, name="atoms")
word_true = tf.placeholder(shape=[None], dtype = tf.int64, name="word_true_index")
keep_prob = tf.placeholder(tf.float32, name = "keep_prob")

h = 0
for i in range(len(weights)):
    L = atoms_placeholder if i == 0 else h
    h = tf.matmul(L, weights[i])+biases[i]
    h = tf.nn.tanh(h) if i == len(weights)-1 else tf.nn.relu(h)
    if i == len(weights)-2:
        h = tf.nn.dropout(h, keep_prob)

norm = tf.sqrt(tf.reduce_sum(tf.square(h), axis=1, keep_dims=True))
embed_predict = (h/norm)
similarity_predict = tf.matmul(embed_predict, tf.transpose(EMBEDDING_TENSOR))
sim_predict_norm = (1+tf.clip_by_value(similarity_predict, 0.01, math.inf))/2
prediction = tf.argmax(similarity_predict,axis=1)

embed_true = tf.nn.embedding_lookup(EMBEDDING_TENSOR, word_true)
similarity = tf.matmul(embed_true, tf.transpose(EMBEDDING_TENSOR))
sim_norm = (1+similarity)/2

cross_entropy = tf.reduce_mean(-tf.reduce_sum(sim_norm * tf.log(sim_predict_norm), 1))
diff_loss = tf.reduce_mean(tf.reduce_sum(tf.square(embed_predict-embed_true)))

tf.summary.scalar("cross_entropy", cross_entropy)
tf.summary.scalar("diff_loss", diff_loss)

# all_vars = tf.trainable_variables()
# vars = [v for v in all_vars if 'vars' in v.name]
# l2_loss = 0
# for v in vars:
#     l2_loss += alpha*tf.nn.l2_loss(v)
#
# tf.summary.scalar("l2_loss", l2_loss)

# pred_word_index = tf.nn.embedding_lookup(EMBEDDING_TENSOR, prediction)
accuracy = 100*tf.reduce_mean(tf.cast(tf.equal(prediction, word_true),tf.float32))
# optim = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy+l2_loss-accuracy)
# optim = tf.train.GradientDescentOptimizer(0.1).minimize(cross_entropy-accuracy)
# optim = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy+l2_loss-accuracy)
optim = tf.train.AdamOptimizer(learning_rate).minimize((cross_entropy/15)+diff_loss - accuracy)