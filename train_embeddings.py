from model_embeddings import *
from sklearn.manifold import TSNE
from matplotlib import pylab
import sys
import shutil

# instance of a tsne thing
tsne = TSNE(perplexity=30.0, n_components=2, init="pca", n_iter=5000)

# progressBar as a string of # signs
def progressBar(counter, size):
    if(counter > size): return ""
    return (counter*"#")+((size-counter)*" ")

# this displays a scatter plot of the embeddings
def plot(embeddings, WORDS):
    assert embeddings.shape[0] >= len(WORDS)
    pylab.figure(figsize=(15,15)) # 15 inches
    for i,label in enumerate(WORDS):
        x, y = embeddings[i,:]
        pylab.scatter(x,y)
        pylab.annotate(label,xy=[x,y],xytext=(5,2),textcoords='offset points',ha='right',va='bottom')
    
    pylab.show()

# loading the dataset
words_dataset = dataset("data/")
# dataset size: 668,597,822
# training
steps = int(7e6)
logStep = 50000
with tf.Session() as sess:
    tf.global_variables_initializer().run()
    # loadModel(sess, LOG_DIR + "model.ckpt")
    shutil.rmtree(LOG_DIR, ignore_errors=True)
    summary_writer = tf.summary.FileWriter(LOG_DIR)
    saveWordsAsMetadata()
    embedding.metadata_path = 'metadata.tsv'
    projector.visualize_embeddings(summary_writer, config)
    train_writer, test_writer = getSummaryWriters(sess)

    startTime = time.time()
    for i in range(steps):
        # batch_labels, batch_targets = process_batch(words_dataset.next_batch(batch_size))
        # print(words_dataset.curFile, words_dataset.c, batch_labels.shape, batch_targets.shape)
        batch = words_dataset.next_batch(batch_size)
        _, lossVal, summary = sess.run([optim, loss, merged_summary], feed_dict={
            train_labels: batch[0], #batch_labels,
            train_targets: batch[1]#batch_targets
        })

        if i % 100:
            train_writer.add_summary(summary, i)
        # now printing progress
        pBarLen = 20
        sys.stdout.write("|%s| - Training(%s/%s)-%s\r"%(progressBar((i//200)%pBarLen, pBarLen),i,steps,
            estimate_time(startTime, steps, i)))

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
                    if k > 0: msg += ", "#"\t"
                    msg += close_word #+ ": %.08f\n"%sim[i,k]
                print(msg)
            print("------------------------------------------")
            saveModel(sess, LOG_DIR+"model.ckpt")
            
            final_embeddings = normalized_embeddings.eval()
            writeToFile(final_embeddings, "savedEmbeddings/embeddings.pkl")
            # plotting using t-SNE
            # two_d_embeddings = tsne.fit_transform(final_embeddings)
            # plot(two_d_embeddings, WORDS)
        
    final_embeddings = normalized_embeddings.eval()
    two_d_embeddings = tsne.fit_transform(final_embeddings)
    plot(two_d_embeddings, WORDS)

    writeToFile(final_embeddings, "savedEmbeddings/embeddings.pkl")