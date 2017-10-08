from embeddingCalc import *
from rnn_reader import *
import sys

EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
WORDS, WORD_TO_NUM = getAllWords()

def trainModel(epochs):
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
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
                embed_series = [data[2]]*TRUNC_BACKPROP_LENGTH
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
                
                # [print(x.shape) for x in input_list]
                for input_batch in input_list:
                    # print(input_batch.shape, len(embed_series))
                    _, _total_loss, _current_state, _embed_predict = sess.run(
                        [train_step, total_loss, current_state, embed_predict_series],
                        feed_dict={
                            ascii_placeholder: input_batch,
                            embedding_placeholder: np.transpose(embed_series),
                            init_state: _current_state
                        }
                    )

                embed_result = _embed_predict[-1]
                loss_list.append(_total_loss)
            print("Epoch %s - Avg.Loss: %.3f"%(ep, sum(loss_list)/VOCAB_SIZE))
            saveModel(sess)
                # print(_embed_predict[-1][-1] - _embed_predict[-1][-2])

if __name__ == "__main__":
    print("training started...")
    trainModel(100)