from ops import *
import random
import math
from tensorflow.contrib.tensorboard.plugins import projector

def getAllWords():
    with open('data/vocabulary.dat') as f:
        words = f.read().splitlines()
    wordList = list(words)
    wordDict = dict()
    for i in range(len(words)):
        wordDict[wordList[i]] = i 
    return [wordList, wordDict]

def saveWordsAsMetadata():
    with open(LOG_DIR+"metadata.tsv", "w") as file:
        file.write("Words\tIndex\n")
        for word in WORDS:
            file.write("%s\t%s\n"%(word, WORDS.index(word)))

# constants
LOG_DIR = "train_log/"
WORDS, wordToNum = getAllWords()
VOCAB_SIZE = len(WORDS)
EMBEDDING_SIZE = 128
valid_set = random.sample(range(VOCAB_SIZE), VOCAB_SIZE//3 if VOCAB_SIZE//3 >= 1 else 1)

# Variables
with tf.variable_scope("vars"):
    embeddings = tf.Variable(
        tf.random_uniform([VOCAB_SIZE, EMBEDDING_SIZE], -1e-4, 1e-4),
        name='embeddings'
    )

    softmax_weights = tf.Variable(
        tf.truncated_normal([VOCAB_SIZE, EMBEDDING_SIZE], stddev=1.0/math.sqrt(EMBEDDING_SIZE)),
        name="weights"
    )

    softmax_biases = tf.Variable(
        tf.zeros([VOCAB_SIZE]),
        name = "biases"
    )

# Placeholders
train_labels = tf.placeholder(tf.int32, [1,batch_size])
train_targets = tf.placeholder(tf.int32, [batch_size, 1])
valid_dataset = tf.constant(valid_set, dtype = tf.int32)

# Model
embed = tf.nn.embedding_lookup(embeddings, train_labels)
loss = tf.reduce_mean(tf.nn.sampled_softmax_loss(
    weights = softmax_weights,
    biases = softmax_biases,
    inputs = tf.cast(train_labels,tf.float32),
    labels = tf.cast(train_targets, tf.float32),
    num_sampled = VOCAB_SIZE//2,
    num_classes = VOCAB_SIZE,
))

optim = tf.train.AdagradOptimizer(0.2).minimize(loss)

norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), 1, keep_dims=True))
normalized_embeddings = embeddings / norm
valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings, valid_dataset)
similarity = tf.matmul(valid_embeddings, tf.transpose(normalized_embeddings))

# tensorboard stuff
# embeddings {
#   tensor_name: 'word_embedding'
#   metadata_path: '$LOG_DIR/metadata.tsv'
# }
config = projector.ProjectorConfig()
embedding = config.embeddings.add()
embedding.tensor_name = embeddings.name

"""
Loss: 18.4618
Wood: Fabric, Plumbing Fixtures, Glass, Project Base Point, Brick
Brick: Survey Point, Casework, Concrete, Soil, Floors
Furniture: Ceramic, Plumbing Fixtures, Survey Point, Windows, Floors
Soil: Survey Point, Brick, Windows, Concrete, Doors
Fabric: Wood, Plumbing Fixtures, Structural Foundations, Windows, Furniture
Casework: Project Base Point, Concrete, Brick, Doors, Ceramic
"""