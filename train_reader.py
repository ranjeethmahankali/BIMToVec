from fc_reader import *
import shutil
import sys

ascii_mat, embed_true, keep_prob = get_placeholders()
embed_predict = reader_model(ascii_mat, keep_prob)
loss, optim = loss_optim(embed_predict, embed_true)
merged = tf.summary.merge_all()

def trainModel(epochs):
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        shutil.rmtree(LOG_DIR, ignore_errors=True)
        train_writer, test_writer = getSummaryWriters(sess)
        start_time = time.time()
        # loadModel(sess)

        for ep in range(epochs):
            i = 0
            while i < VOCAB_SIZE:
                j = min(i+WORD_BATCH_SIZE, VOCAB_SIZE)
                words = WORDS[i : j]
                batch = prepWordBatch(words)

                _ , summary = sess.run([optim,merged], feed_dict={
                    ascii_mat: batch[0],
                    embed_true: batch[1],
                    keep_prob:0.5
                })

                if i%40 == 0:
                    train_writer.add_summary(summary, (ep*VOCAB_SIZE)+i)
                    batch = prepWordBatch(TEST_WORDS)
                    summary = sess.run(merged, feed_dict={
                        ascii_mat: batch[0],
                        embed_true: batch[1],
                        keep_prob:1
                    })
                    test_writer.add_summary(summary, (ep * VOCAB_SIZE) + i)
                
                sys.stdout.write("...Training... - (%s/%s) - %s\r"%(
                    ep*VOCAB_SIZE + i,
                    epochs*VOCAB_SIZE,
                    estimate_time(start_time, epochs*VOCAB_SIZE, ep*VOCAB_SIZE + i)
                ))

                i += WORD_BATCH_SIZE
                # print(i)
            if ep % 20 == 0:
                saveModel(sess, silent = True)
        saveModel(sess)

if __name__ == "__main__":
    print("Beginning training...")
    trainModel(20000)