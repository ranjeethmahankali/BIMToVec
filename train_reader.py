from reader_model import *
import sys
import shutil
import random

WORDS, WORD_TO_NUM = getAllWords()
ATOMS, ATOM_TO_NUM = getAllAtoms()

TEST_WORDS = random.sample(WORDS, batch_size)

TRAIN_WORDS = [w for w in WORDS if True]#not w in TEST_WORDS]


EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
ATOM_EMBED = loadFromFile("savedEmbeddings/atom_embeddings.pkl")

def prepare_word(w):
    a_set = []
    for a in ATOMS:
        if a in w and len(a_set) < ATOM_NUM:
            a_set.append(ATOM_EMBED[ATOM_TO_NUM[a]])

    if len(a_set) == 0:
        return [None, None]
    while len(a_set) < ATOM_NUM:
        a_set += a_set

    if len(a_set) > ATOM_NUM:
        a_set = a_set[:ATOM_NUM]

    arr = np.reshape(np.array(a_set), [1, -1])
    return [np.concatenate([arr, get_char_list_vec(w)], axis = 1), WORD_TO_NUM[w]]

global_counter = 0
def next_batch(num):
    global global_counter
    a_batch = None
    w_batch = []
    i = 0
    while i < num:
        w = TRAIN_WORDS[(global_counter+num)%len(TRAIN_WORDS)]
        global_counter = (global_counter+1)%len(TRAIN_WORDS)
        arr, word_embed = prepare_word(w)
        if arr is None or word_embed is None:
            continue

        if a_batch is None:
            a_batch = arr
        else:
            a_batch = np.concatenate([a_batch, arr], axis = 0)

        w_batch.append(word_embed)
        i += 1

    return [a_batch, w_batch]

def make_test_batch():
    a_batch = None
    w_batch = []
    for w in TEST_WORDS:
        arr, word_embed = prepare_word(w)
        if arr is None or word_embed is None:
            continue

        if a_batch is None:
            a_batch = arr
        else:
            a_batch = np.concatenate([a_batch, arr], axis=0)

        w_batch.append(word_embed)

    return [a_batch, w_batch]

TEST_BATCH = make_test_batch()
        

merged_summary = tf.summary.merge_all()
steps = 3210
logStep = steps//32
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    # loadModel(sess)
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    train_writer, test_writer = getSummaryWriters(sess)

    startTime = time.time()
    for i in range(steps):
        batch = next_batch(batch_size)
        _, _loss, _acc, _pred, _summary = sess.run([optim, diff_loss, accuracy, prediction,
                                             merged_summary],
        feed_dict={
            atoms_placeholder: batch[0],
            word_true: batch[1],
            keep_prob: 1.0
        })

        if i % logStep == 0:
            # print(batch[1], _pred)
            print("Loss: %s; Acc: %.2f"%(_loss, _acc))
            if i > 0:
                saveModel(sess, silent=True)
            train_writer.add_summary(_summary, i)

        if i % (2*logStep) == 0:
            _loss, _summary = sess.run([cross_entropy, merged_summary], feed_dict={
                atoms_placeholder: TEST_BATCH[0],
                word_true:TEST_BATCH[1],
                keep_prob:1.0
            })
            test_writer.add_summary(_summary, i)

        sys.stdout.write("...Training-%s-(%s / %s)-%s\r"%(
            progress_bar(20, (i%20)+1),
            i, steps,
            estimate_time(startTime, steps, i)
        ))
    saveModel(sess)