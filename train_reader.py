from reader_model import *
import sys
import shutil

atoms, word_true, keep_prob = get_placeholders()
word_predict = reader_model(atoms, keep_prob)
loss, optim = loss_optim(word_predict, word_true)

WORDS, WORD_TO_NUM = getAllWords()
ATOMS, ATOM_TO_NUM = getALlAtoms()
EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
ATOM_EMBED = loadFromFile("savedEmbeddings/atom_embeddings.pkl")

global_counter = 0
def next_batch(num):
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

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())