from reader_model import *
from embeddingCalc import *


ATOMS, ATOM_TO_NUM = getAllAtoms()
ATOM_EMBED = loadFromFile("savedEmbeddings/atom_embeddings.pkl")

def atoms_in_word(word):
    atom_embeddings = []
    for atom in ATOMS:
        if atom in word:
            atom_embeddings.append(ATOM_EMBED[ATOM_TO_NUM[atom]])

    if len(atom_embeddings) == 0:
        return np.zeros([1,(ATOM_NUM*ATOM_SIZE)+(WORD_SAMPLE_SIZE)])

    while len(atom_embeddings) < ATOM_NUM:
        atom_embeddings += atom_embeddings

    if len(atom_embeddings) > ATOM_NUM:
        atom_embeddings = atom_embeddings[:ATOM_NUM]

    return np.concatenate([np.reshape(np.array(atom_embeddings), [1,-1]), get_char_list_vec(word)], axis=1)

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    loadModel(sess)
    while True:
        _word = input("Enter word: ")
        embed_atoms = atoms_in_word(_word)
        result = sess.run(prediction, feed_dict={
            atoms_placeholder: embed_atoms,
            keep_prob:1.0
        })
        interpretation = WORDS[result[0]]
        print(interpretation)
