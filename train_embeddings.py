from model_embeddings import *
from sklearn.manifold import TSNE
from matplotlib import pylab

# converts from strings to numbers
def process_batch(batch):
    labels = []
    targets = []
    for w in batch[0]:
        labels.append(wordToNum[w])
    
    for w in batch[1]:
        targets.append(wordToNum[w])

    return [np.expand_dims(labels,0), np.expand_dims(targets, 1)]

# loading the dataset
words_dataset = dataset("data/")
# training
steps = 1000000
logStep = 10000
with tf.Session() as sess:
    tf.global_variables_initializer().run()
    for i in range(steps):
        batch_labels, batch_targets = process_batch(words_dataset.next_batch(batch_size))
        _, lossVal = sess.run([optim, loss], feed_dict={
            train_labels: batch_labels,
            train_targets: batch_targets
        })

        if i % logStep == 0:
            print("Loss: %s" % lossVal)
            sim = similarity.eval()
            for i in range(len(valid_set)):
                word = WORDS[valid_set[i]]
                top_k = 5
                nearest = (-sim[i,:]).argsort()[1:1+top_k]
                msg = "%s: "% word
                for k in range(top_k):
                    close_word = WORDS[nearest[k]]
                    if k > 0: msg += ", "
                    msg += close_word
                print(msg)
            print("------------------------------------------")
            saver = tf.train.Saver()
            saver.save(sess, LOG_DIR+"model.ckpt")
    
    final_embeddings = normalized_embeddings.eval()

# plotting using t-SNE
tsne = TSNE(perplexity=30.0, n_components=2, init="pca", n_iter=5000)
two_d_embeddings = tsne.fit_transform(final_embeddings)

def plot(embeddings, labels):
    assert embeddings.shape[0] >= len(labels)
    pylab.figure(figsize=(15,15)) # 15 inches
    for i,label in enumerate(labels):
        x, y = embeddings[i,:]
        pylab.scatter(x,y)
        pylab.annotate(label,xy=[x,y],xytext=(5,2),textcoords='offset points',ha='right',va='bottom')
    
    pylab.show()

plot(two_d_embeddings, WORDS)