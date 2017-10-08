from ops import *
from embeddingCalc import *
from model_embeddings import EMBEDDING_SIZE, VOCAB_SIZE

TRUNC_BACKPROP_LENGTH = 8
BATCH_SIZE = 1
STATE_SIZE = 6
NUM_LAYERS = 4
EPOCH_NUM = 100

ascii_placeholder = tf.placeholder(tf.float32, [BATCH_SIZE, TRUNC_BACKPROP_LENGTH])
embedding_placeholder = tf.placeholder(tf.float32, [EMBEDDING_SIZE, TRUNC_BACKPROP_LENGTH])

init_state = tf.placeholder(tf.float32, [NUM_LAYERS, 2, BATCH_SIZE, STATE_SIZE])
state_per_layer_list = tf.unstack(init_state, axis = 0)
rnn_tuple_state = tuple(
    [tf.nn.rnn_cell.LSTMStateTuple(state_per_layer_list[i][0], state_per_layer_list[i][1]) for i in range(NUM_LAYERS)]
)

W2 = tf.Variable(np.random.rand(STATE_SIZE, EMBEDDING_SIZE), dtype = tf.float32)
B2 = tf.Variable(np.zeros([1,EMBEDDING_SIZE]), dtype=tf.float32)

# unpack columns
input_series = tf.split(ascii_placeholder,TRUNC_BACKPROP_LENGTH,axis = 1)
target_series = tf.unstack(embedding_placeholder, axis=1)
# [print(target.get_shape()) for target in target_series]
# Forward pass

stacked_rnn = []
for iiLyr in range(NUM_LAYERS):
    stacked_rnn.append(tf.nn.rnn_cell.LSTMCell(STATE_SIZE, state_is_tuple=True))
multiCell = tf.nn.rnn_cell.MultiRNNCell(cells=stacked_rnn, state_is_tuple=True)

states_series, current_state = tf.nn.static_rnn(multiCell, input_series, initial_state = rnn_tuple_state)

logits_series = [
        tf.reduce_mean(tf.transpose(tf.matmul(state, W2)+B2), axis=1) for state in states_series
    ]
embed_predict_series = [logits/tf.norm(logits) for logits in logits_series]
# [print(tensor.get_shape()) for tensor in logits_series]

losses = [tf.reduce_sum(tf.abs(logits-output))
            for logits, output in zip(logits_series, target_series)]
total_loss = tf.reduce_mean(losses)

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