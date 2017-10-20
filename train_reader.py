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
    ws = WORDS[global_counter: global_counter+num]
    a_batch = []
    w_batch = []
    for w in ws:
        a_set = []
        for a in ATOMS:
            if a in w and len(a_set) < ATOM_NUM:
                a_set.append(ATOM_EMBED[ATOM_TO_NUM[a]])
        
        while len(a_set) < ATOM_NUM:
            a_set += a_set
        
        if len(a_set) > ATOM_NUM:
            a_set = a_set[:ATOM_NUM]
        
        a_batch.append(np.reshape(np.array(a_set), [1,-1]))
        w_batch.append(EMBEDDINGS[WORD_TO_NUM[w]])
    
    global_counter = (global_counter+num)%len(WORDS)
    return [a_batch, w_batch]
        

merged_summary = tf.summary.merge_all()
steps = 100000
logStep = steps//100
with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    # loadModel(sess)
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    train_writer, test_writer = getSummaryWriters(sess)

    startTime = time.time()
    for i in range(steps):
        batch = next_batch(batch_size)
        _, _loss, _summary = sess.run([optim, loss, merged_summary],
        feed_dict={
            atoms: batch[0],
            word_true: batch[1],
            keep_prob: 0.5
        })

        if i % logStep == 0:
            print("Loss: %s"%_loss)
            if i > 0:
                saveModel(sess)
            train_writer.add_summary(summary, i)

        print("...Training-%s-(%s/%s)-%s\r"%(
            progress_bar(20, (i%20)+1)),
            i, steps,
            estimate_time(startTime, steps, i)
        )
    saveModel(sess)