from reader_model import *
import sys
import shutil

atoms, word_true, keep_prob = get_placeholders()
word_predict = reader_model(atoms, keep_prob)
loss, optim = loss_optim(word_predict, word_true)

merged_summary = tf.summary.merge_all()

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())