from rnn_reader import *
from embeddingCalc import *

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    loadModel(sess)

    while True:
        word = input("Enter the word: ")
        data = prepareWord(word, training = False)
        if len(data) == 0:
            continue

        _current_state = np.zeros([NUM_LAYERS, 2, BATCH_SIZE, STATE_SIZE])
        # print(_current_state.shape)
        n = 0
        ascii_series = np.array(data)
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
            _current_state, _embed_predict = sess.run(
                [current_state, embed_predict_series],
                feed_dict={
                    ascii_placeholder: input_batch,
                    init_state: _current_state,
                    keep_prob:1
                }
            )
        embed_result = _embed_predict[-1]
        print(toEnglish(embed_result,3))