from ops import *
import random

ATOM_NUM = 5
ATOM_SIZE = 32
WORD_SIZE = 64
WORD_SAMPLE_SIZE = 20

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")

def get_placeholders():
    atoms = tf.placeholder(shape=[None, (ATOM_NUM*ATOM_SIZE)+WORD_SAMPLE_SIZE], dtype = tf.float32, name="atoms")
    word = tf.placeholder(shape=[None, WORD_SIZE], dtype = tf.float32, name="word")
    keep_prob = tf.placeholder(tf.float32, name = "keep_prob")
    return [atoms, word, keep_prob]

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

LAYERS = [(ATOM_NUM*ATOM_SIZE)+WORD_SAMPLE_SIZE, 1280, 320, 1280, WORD_SIZE]

with tf.variable_scope("vars"):
    weights = [
        weightVariable([LAYERS[i], LAYERS[i+1]], name="w%s"%i) for i in range(len(LAYERS)-1)
    ]

    biases = [
        biasVariable([LAYERS[i+1]], name="b%s"%i) for i in range(len(LAYERS)-1)
    ]

def reader_model(atoms, keep_prob):
    h = 0
    for i in range(len(weights)):
        L = atoms if i == 0 else h
        h = tf.matmul(L, weights[i])+biases[i]
        h = tf.nn.tanh(h) if i == len(weights)-1 else lrelu(h)
        if i == len(weights)-2:
            h = tf.nn.dropout(h, keep_prob)

    norm = tf.sqrt(tf.reduce_sum(tf.square(h), axis=1, keep_dims=True))
    return (h/norm)

def loss_optim(word_guess, word_true):
    #similarity = tf.matmul(word_true, tf.transpose(word_guess))
    #loss = -tf.reduce_sum(tf.diag(similarity))
    loss = tf.reduce_sum(tf.abs(word_guess - word_true))

    tf.summary.scalar("loss", loss)

    all_vars = tf.trainable_variables()
    vars = [v for v in all_vars if 'vars' in v.name]
    l2_loss = 0
    for v in vars:
        l2_loss += alpha*tf.nn.l2_loss(v)

    tf.summary.scalar("l2_loss", l2_loss)

    optim = tf.train.AdamOptimizer(learning_rate).minimize(loss+l2_loss)

    return loss, optim