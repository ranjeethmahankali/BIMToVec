from ops import *
from model_embeddings import EMBEDDING_SIZE

TRUNC_BACKPROP_LENGTH = 15
ASCII_VEC_DIM = 8
STATE_SIZE = 6
NUM_LAYERS = 4

ascii_placeholder = tf.placeholder(tf.flot32, [ASCII_VEC_DIM, TRUNC_BACKPROP_LENGTH])
embedding_placeholder = tf.placeholder(tf.flot32, [EMBEDDING_SIZE, TRUNC_BACKPROP_LENGTH])

init_state = tf.placeholder(tf.float32, [NUM_LAYERS, 2, ASCII_VEC_DIM, STATE_SIZE])
state_per_layer_list = tf.unpack(init_state, axis = 0)
rnn_tuple_state = tuple(
    [tf.nn.rnn_cell.LSTMStateTuple(state_per_layer_list[i][0], state_per_layer_list[i][1]) for i in range(NUM_LAYERS)]
)

W2 = tf.Variable(np.random.rand(STATE_SIZE, EMBEDDING_SIZE), dtype = tf.float32)
B2 = tf.Variable(np.zeros([1,EMBEDDING_SIZE]), dtype=tf.float32)

# unpack columns
input_series = tf.split(ascii_placeholder,TRUNC_BACKPROP_LENGTH,1)
output_series = tf.unpack(embedding_placeholder, axis=1)

# Forward pass
cell = tf.nn.rnn_cell.LSTMCell(STATE_SIZE, state_is_tuple=True)
cell = tf.nn.rnn_cell.MultiRNNCell([cell]*NUM_LAYERS, state_is_tuple=True)
states_series, current_state = tf.nn.rnn(cell, input_series, initial_state = rnn_tuple_state)

logits_series = [tf.matmul(state, W2)+B2 for state in states_series]
embed_predict_series = [logits/tf.norm(logits) for logits in logits_series]

losses = [-tf.mul(logits, output) for logits, output in zip(logits_series, output_series)]
total_loss = tf.reduce_mean(losses)

train_step = tf.train.AdagradOptimizer(0.3).minimize(total_loss)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    loss_list = []
    
_current_state = np.zeros([NUM_LAYERS, 2, ASCII_VEC_DIM, STATE_SIZE])
