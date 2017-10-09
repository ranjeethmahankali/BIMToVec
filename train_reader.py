from embeddingCalc import *
from rnn_reader import *
import sys
import shutil

EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
WORDS, WORD_TO_NUM = getAllWords()
merged = tf.summary.merge_all()

def trainModel(epochs):
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        shutil.rmtree(LOG_DIR, ignore_errors=True)
        train_writer, test_writer = getSummaryWriters(sess)
        start_time = time.time()
        # loadModel(sess)
        for ep in range(epochs):
            loss_list = []
            for i in range(VOCAB_SIZE):
                data = prepareWord(WORDS[i])
                if len(data[1]) == 0:
                    continue

                _current_state = np.zeros([NUM_LAYERS, 2, BATCH_SIZE, STATE_SIZE])
                # print(_current_state.shape)
                n = 0
                embed_series = np.array([data[2]]*TRUNC_BACKPROP_LENGTH)
                ascii_series = np.array(data[1])
                ascii_series = np.reshape(ascii_series, [BATCH_SIZE,-1])

                num = ascii_series.shape[1]%TRUNC_BACKPROP_LENGTH
                # print(ascii_series.shape, num)
                if num > 0:
                    ascii_series = np.concatenate(
                        [ascii_series, np.zeros([BATCH_SIZE, TRUNC_BACKPROP_LENGTH-num])],axis = 1)
                
                # print(ascii_series.shape)
                input_list = np.split(ascii_series, 
                    ascii_series.shape[1]/TRUNC_BACKPROP_LENGTH, axis=1)
                
                # print(embed_series.shape)
                # [print(x.shape) for x in input_list]
                for input_batch in input_list:
                    # print(input_batch.shape, len(embed_series))
                    _, _total_loss, _current_state, _embed_predict, _summary = sess.run(
                        [train_step, total_loss, current_state, embed_predict_series, merged],
                        feed_dict={
                            ascii_placeholder: input_batch,
                            embedding_placeholder: np.transpose(embed_series),
                            init_state: _current_state,
                            keep_prob: 0.5
                        }
                    )

                embed_result = _embed_predict[-1]
                loss_list.append(_total_loss)

                if i%10 == 0:
                    train_writer.add_summary(_summary, (VOCAB_SIZE*ep)+i)
                
                sys.stdout.write("...Training...%s - (%s/%s) - %s\r"%(
                    progress_bar(20, (i%20)+1),
                    ep*VOCAB_SIZE + i,
                    epochs*VOCAB_SIZE,
                    estimate_time(start_time, epochs*VOCAB_SIZE, ep*VOCAB_SIZE + i)
                ))

            print("Epoch %s - Avg.Loss: %.3f"%(ep, sum(loss_list)/VOCAB_SIZE))
            saveModel(sess, silent = True)
        saveModel(sess)
                # print(_embed_predict[-1][-1] - _embed_predict[-1][-2])

if __name__ == "__main__":
    print("Beginning training...")
    trainModel(500)