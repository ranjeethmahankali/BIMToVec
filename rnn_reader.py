from ops import *
from model_embeddings import EMBEDDING_SIZE

TRUNC_BACKPROP_LENGTH = 15
ASCII_VEC_DIM = 8
STATE_SIZE = 6

ascii_placeholder = tf.placeholder(tf.flot32, [ASCII_VEC_DIM, TRUNC_BACKPROP_LENGTH])
embedding_placeholder = tf.placeholder(tf.flot32, [EMBEDDING_SIZE, TRUNC_BACKPROP_LENGTH])

