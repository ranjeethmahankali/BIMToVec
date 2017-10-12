from fc_reader import *
from embeddingCalc import *

ascii_mat, embed_true, keep_prob = get_placeholders()
embed_predict = reader_model(ascii_mat, keep_prob)
# loss, optim = loss_optim(embed_predict, embed_true)
# merged = tf.summary.merge_all()

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    loadModel(sess)

    while True:
        word = input("Enter the word: ")
        wordArr = prepareWord(word)
        
        _embedding = sess.run(embed_predict, feed_dict={
            ascii_mat: [wordArr],
            keep_prob:1.0
        })

        embed_result = _embedding[0]
        print(toEnglish(embed_result,3))