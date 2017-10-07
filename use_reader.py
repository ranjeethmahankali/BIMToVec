from rnn_reader import *
from embeddingCalc import *

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    loadModel(sess)

    while True:
        word = input("Enter the word: ")
        data = prepareWord(word, training = False)
        _current_state = np.zeros([NUM_LAYERS, 2, ASCII_VEC_DIM, STATE_SIZE])
        # print(_current_state.shape)
        n = 0
        while n < len(data):
            ascii_series = None
            # print(n, TRUNC_BACKPROP_LENGTH, n+TRUNC_BACKPROP_LENGTH, len(data))
            if (n + TRUNC_BACKPROP_LENGTH) < len(data):
                ascii_series = data[1][n:n+TRUNC_BACKPROP_LENGTH]
            else:
                batch_data = np.array(data[n:])
                padding = np.zeros([n+TRUNC_BACKPROP_LENGTH- len(data), ASCII_VEC_DIM])
                # print(batch_data.shape, padding.shape)
                ascii_series = np.concatenate([batch_data, padding], axis=0)

            _current_state, _embed_predict = sess.run(
                [current_state, embed_predict_series],
                feed_dict={
                    ascii_placeholder: np.transpose(ascii_series),
                    init_state: _current_state
                }
            )

            n += TRUNC_BACKPROP_LENGTH

        embed_result = _embed_predict[-1]
        print(toEnglish(embed_result,3))