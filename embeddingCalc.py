from ops import *
import math
import random
from matplotlib import pylab
from sklearn.manifold import TSNE

# instance of a tsne thing
tsne = TSNE(perplexity=30.0, n_components=2, init="pca", n_iter=5000)
#saved words and embeddings
EMBEDDINGS = loadFromFile("savedEmbeddings/embeddings.pkl")
WORDS, WORD_TO_NUM = getAllWords()

def normalize(vector):
    norm = np.sqrt(np.square(vector).sum())
    if norm == 0:
        return vector
    else:
        return vector/norm

def nearest(testEmbedding,numNearest = 1, skipFirst = True):
    similarity = np.matmul(testEmbedding, np.transpose(EMBEDDINGS))
    k = 1 if skipFirst else 0
    matches = (-similarity).argsort()[k:numNearest+k]
    # print(matches.shape)
    matchWords = []
    # print(matches.shape)
    for n in matches:
        matchWords.append(WORDS[n])

    return matchWords

def nearestToWord(word, numNearest = 1):
    testEmbedding = toEmbedding(word)
    return nearest(testEmbedding, numNearest)

def toEmbedding(word):
    return EMBEDDINGS[WORD_TO_NUM[word]]

def toEnglish(embed, nearest_k = 1):
    if nearest_k == 1:
        return nearest(embed, nearest_k, skipFirst = False)[0]
    else:
        return nearest(embed, nearest_k, skipFirst = False)

# A is to B as C is to what ? this function returns the answer for this
def Extrapolate(A, B, C):    
    # calculate C - A + B
    diff = toEmbedding(A) - toEmbedding(B)
    return toEnglish(normalize(toEmbedding(C) - diff))

# this scores the belong together ness of the given collection of ifc names belong together
def coherence(words):
    for wset in words:
        for word in wset:
            if not word in WORDS:
                raise ValueError("Word %s not found"%word)

    embeds = []
    for wset in words:
        w_embeds = []
        for word in wset:
            w_embeds.append(toEmbedding(word))
        w_embeds = np.array(w_embeds)
        embeds.append(np.mean(w_embeds, axis=0))
    
    embeds = np.array(embeds)
    cosineDist = np.matmul(embeds, np.transpose(embeds))
    avgDistances = (np.sum(cosineDist, axis=1) - 1)/(len(words)-1)
    avgDist = np.mean(avgDistances)
    return avgDistances, avgDist

def oddOneOut(words):
    words = [[word for word in wset if word in WORDS] for wset in words]
    distances, avg = coherence(words)
    return words, np.argmin(distances)

# this displays a scatter plot of the embeddings
def plot(embeddings, WORDS):
    assert len(embeddings) >= len(WORDS)
    pylab.figure(figsize=(15,15)) # 15 inches
    for i,label in enumerate(WORDS):
        x, y = embeddings[i,:]
        pylab.scatter(x,y)
        pylab.annotate(label,xy=[x,y],xytext=(5,2),textcoords='offset points',ha='right',va='bottom')
    
    pylab.show()
        

# the main program starts here
# MEAN_COHERENCE = coherence(WORDS)
# print("mean coherence: %s"%MEAN_COHERENCE)
# # print(WORDS[min1], WORDS[min2])
# print(coherence(["IfcWallStandardCase", "IfcGrid"]))
# print(coherence(["IfcWall", "IfcDoor"]))
if __name__ == "__main__":
    indices = random.sample(range(len(WORDS)), 650)
    words = [(WORDS[i] if len(WORDS[i]) < 15 else WORDS[i][:20]) for i in indices]
    embeds = [EMBEDDINGS[i] for i in indices]
    embeds_2d = tsne.fit_transform(embeds)
    plot(embeds_2d, words)
    # print(Extrapolate("ifcpile", "concreteprecastconcretenormalweightksi", "ifcstair"))
