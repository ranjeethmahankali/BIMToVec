from ops import *

ATOM_NUM = 5
ATOM_SIZE = 32
WORD_SIZE = 64

def get_placeholders():
    atoms = tf.placeholder(shape=[None, ATOM_NUM*ATOM_SIZE], dtype = tf.float32, name="atoms")
    word = tf.placeholder(shape=[None, WORD_SIZE], dtype = tf.float32, name="word")
    keep_prob = tf.placeholder(tf.float32, name = "keep_prob")
    return [atoms, word, keep_prob]

LAYERS = [ATOM_NUM*ATOM_SIZE, 320, 640, 1280, 512, 256, WORD_SIZE]

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
        h = tf.nn.tanh(h) if i == len(weights)-1 else tf.nn.relu(h)
        if i == len(weights)-2:
            h = tf.nn.dropout(h, keep_prob)
    
    return h

def loss_optim(word_guess, word_true):
    similarity = tf.matmul(word_true, tf.transpose(word_guess))
    loss = -tf.reduce_sum(tf.diag(similarity))

    tf.summary.scalar("loss", loss)

    all_vars = tf.trainable_variables()
    vars = [v for v in all_vars if 'vars' in v.name]
    l2_loss = 0
    for v in vars:
        l2_loss += alpha*tf.nn.l2_loss(v)

    optim = tf.train.AdamOptimizer(learning_rate).minimize(loss+l2_loss)

    return loss, optim