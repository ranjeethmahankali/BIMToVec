from embeddingCalc import *
from rnn_reader import *
import sys

EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
WORDS, WORD_TO_NUM = getAllWords()

# convert a character to ascii code (8 bits)
def prepareChar(ch):
    if len(ch) != 1:
        raise ValueError("Please supply a single character for the ascii lookup")
    binStr = "{0:08b}".format(ord(ch))
    binList = []
    for d in binStr:
        binList.append(int(d))
    
    return binList

# converts a word into an ascii matrix and ignores non alphabets
def prepareWord(word):
    asciiList = []
    for ch in word:
        if not ch.isalpha():
            continue
        asciiList.append(prepareChar(ch))
    
    batchSize = len(asciiList)
    return [batchSize, asciiList, toEmbedding(word)]

def trainModel(epochs):
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # loadModel()
        for ep in range(epochs):
            loss_list = []
            for i in range(VOCAB_SIZE):
                data = prepareWord(WORDS[i])
                _current_state = np.zeros([NUM_LAYERS, 2, ASCII_VEC_DIM, STATE_SIZE])
                # print(_current_state.shape)
                n = 0
                embed_series = [data[2]]*TRUNC_BACKPROP_LENGTH
                while n < data[0]:
                    ascii_series = None
                    if n + TRUNC_BACKPROP_LENGTH < data[0]:
                        ascii_series = data[1][n:n+TRUNC_BACKPROP_LENGTH]
                    else:
                        batch_data = np.array(data[1][n:])
                        padding = np.zeros([n+TRUNC_BACKPROP_LENGTH- data[0], ASCII_VEC_DIM])
                        # print(batch_data.shape, padding.shape)
                        ascii_series = np.concatenate([batch_data, padding], axis=0)

                    _, _total_loss, _current_state, _embed_predict = sess.run(
                        [train_step, total_loss, current_state, embed_predict_series],
                        feed_dict={
                            ascii_placeholder: np.transpose(ascii_series),
                            embedding_placeholder: np.transpose(embed_series),
                            init_state: _current_state
                        }
                    )

                    n += TRUNC_BACKPROP_LENGTH

                embed_result = _embed_predict[-1]
                loss_list.append(_total_loss)
            print("Epoch %s - Avg.Loss: %.3f"%(ep, sum(loss_list)/VOCAB_SIZE))
            saveModel()
                # print(_embed_predict[-1][-1] - _embed_predict[-1][-2])

if __name__ == "__main__":
    print("training started...")
    trainModel(500)