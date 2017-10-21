from reader_model import *
import sys
import shutil

atoms, word_true, keep_prob = get_placeholders()
word_predict = reader_model(atoms, keep_prob)
loss, optim = loss_optim(word_predict, word_true)

WORDS, WORD_TO_NUM = getAllWords()
ATOMS, ATOM_TO_NUM = getAllAtoms()
EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
ATOM_EMBED = loadFromFile("savedEmbeddings/atom_embeddings.pkl")

global_counter = 0
def next_batch(num):
    global global_counter
    a_batch = None
    w_batch = []
    i = 0
    while i < num:
        w = WORDS[(global_counter+num)%len(WORDS)]
        global_counter = (global_counter+1)%len(WORDS)
        a_set = []
        for a in ATOMS:
            if a in w and len(a_set) < ATOM_NUM:
                a_set.append(ATOM_EMBED[ATOM_TO_NUM[a]])
        
        if len(a_set) == 0:
            continue
        while len(a_set) < ATOM_NUM:
            a_set += a_set
        
        if len(a_set) > ATOM_NUM:
            a_set = a_set[:ATOM_NUM]

        arr = np.reshape(np.array(a_set), [1,-1])
        if a_batch is None:
            a_batch = arr
        else:
            a_batch = np.concatenate([a_batch, arr], axis = 0)

        w_batch.append(EMBEDDINGS[WORD_TO_NUM[w]])
        i += 1

    return [a_batch, w_batch]
        

merged_summary = tf.summary.merge_all()
steps = 48000
logStep = steps//100
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    loadModel(sess)
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    train_writer, test_writer = getSummaryWriters(sess)

    startTime = time.time()
    for i in range(steps):
        batch = next_batch(batch_size)
        _, _loss, _summary = sess.run([optim, loss, merged_summary],
        feed_dict={
            atoms: batch[0],
            word_true: batch[1],
            keep_prob: 1.0
        })

        if i % logStep == 0:
            print("Loss: %s"%_loss)
            if i > 0:
                saveModel(sess)
            train_writer.add_summary(_summary, i)

        sys.stdout.write("...Training-%s-(%s / %s)-%s\r"%(
            progress_bar(20, (i%20)+1),
            i, steps,
            estimate_time(startTime, steps, i)
        ))
    saveModel(sess)