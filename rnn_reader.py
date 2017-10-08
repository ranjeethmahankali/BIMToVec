from ops import *
from embeddingCalc import *
from model_embeddings import EMBEDDING_SIZE, VOCAB_SIZE

TRUNC_BACKPROP_LENGTH = 8
BATCH_SIZE = 1
STATE_SIZE = 6
NUM_LAYERS = 4
EPOCH_NUM = 100

HIDDEN_DIM_1 = 12
HIDDEN_DIM_2 = 16
HIDDEN_DIM_3 = 32
HIDDEN_DIM_4 = 48
OUTPUT_DIM = 64

with tf.variable_scope('fullyConnected'):
    w1 = weightVariable([STATE_SIZE, HIDDEN_DIM_1], 'w1')
    b1 = weightVariable([1, HIDDEN_DIM_1], 'b1')
    w2 = weightVariable([HIDDEN_DIM_1, HIDDEN_DIM_2], 'w2')
    b2 = weightVariable([1, HIDDEN_DIM_2], 'b2')
    w3 = weightVariable([HIDDEN_DIM_2, HIDDEN_DIM_3], 'w3')
    b3 = weightVariable([1, HIDDEN_DIM_3], 'b3')
    w4 = weightVariable([HIDDEN_DIM_3, HIDDEN_DIM_4], 'w4')
    b4 = weightVariable([1, HIDDEN_DIM_4], 'b4')
    w5 = weightVariable([HIDDEN_DIM_4, OUTPUT_DIM], 'w5')
    b5 = weightVariable([1, OUTPUT_DIM], 'b5')

def l2_loss():
    all_vars = tf.trainable_variables()
    var_list = [v for v in all_vars if 'fully' in v.name]
    l2_loss = 0
    for v in var_list:
        l2_loss += tf.nn.l2_loss(v)
    
    return l2_loss

def fullyConnected(state, keep_prob):
    h1 = tf.nn.relu(tf.matmul(state,w1) + b1)
    h2 = tf.nn.relu(tf.matmul(h1, w2) + b2)
    h3 = tf.nn.relu(tf.matmul(h2, w3) + b3)
    h4 = tf.nn.relu(tf.matmul(h3, w4) + b4)
    
    h4_drop = tf.nn.dropout(h4, keep_prob)
    output = tf.nn.sigmoid(tf.matmul(h4_drop, w5) + b5)
    # return tf.transpose(output)
    return output

ascii_placeholder = tf.placeholder(tf.float32, [BATCH_SIZE, TRUNC_BACKPROP_LENGTH])
embedding_placeholder = tf.placeholder(tf.float32, [EMBEDDING_SIZE, TRUNC_BACKPROP_LENGTH])
keep_prob = tf.placeholder(tf.float32)
init_state = tf.placeholder(tf.float32, [NUM_LAYERS, 2, BATCH_SIZE, STATE_SIZE])

state_per_layer_list = tf.unstack(init_state, axis = 0)
rnn_tuple_state = tuple(
    [tf.nn.rnn_cell.LSTMStateTuple(state_per_layer_list[i][0], state_per_layer_list[i][1]) for i in range(NUM_LAYERS)]
)

# unpack columns
input_series = tf.split(ascii_placeholder,TRUNC_BACKPROP_LENGTH,axis = 1)
target_series = tf.unstack(embedding_placeholder, axis=1)
# [print(target.get_shape()) for target in target_series]
# Forward pass

stacked_rnn = []
for iiLyr in range(NUM_LAYERS):
    stacked_rnn.append(tf.nn.rnn_cell.LSTMCell(STATE_SIZE, state_is_tuple=True))
multiCell = tf.nn.rnn_cell.MultiRNNCell(cells=stacked_rnn, state_is_tuple=True)

states_series, current_state = tf.nn.static_rnn(multiCell, input_series, 
                                    initial_state = rnn_tuple_state)

embed_predict_series = [
        fullyConnected(state, keep_prob) for state in states_series
    ]
# [print(tensor.get_shape()) for tensor in embed_predict_series]

losses = [tf.reduce_sum(tf.abs(tf.transpose(output)-target))
            for output, target in zip(embed_predict_series, target_series)]
# total_loss = tf.reduce_mean(losses)
total_loss = tf.reduce_mean(losses) + (l2_loss()*alpha)

train_step = tf.train.AdamOptimizer(1e-4).minimize(total_loss)
# train_step = tf.train.AdagradOptimizer(0.3).minimize(total_loss)

############ Now writing functions to process input for the RNN
CHAR_LIST = list("abcdefghijklmnopqrstuvwxyz")

# converts a word into an ascii matrix and ignores non alphabets
def prepareWord(word, training = True):
    global CHAR_LIST
    charNum = len(CHAR_LIST)
    converted = []
    for ch in word:
        if not ch in CHAR_LIST:
            continue
        converted.append((CHAR_LIST.index(ch)+1)/charNum)
    
    batchSize = len(converted)
    if training:
        return [batchSize, converted, toEmbedding(word)]
    else:
        return converted