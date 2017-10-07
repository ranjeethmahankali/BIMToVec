from ops import *
from model_embeddings import getAllWords
import math

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
    # print(matches)
    matchWords = []
    for n in matches:
        matchWords.append(WORDS[n])

    return matchWords

def nearestToWord(word, numNearest = 1):
    testEmbedding = toEmbedding(word)
    return nearest(testEmbedding, numNearest)

def toEmbedding(word):
    return EMBEDDINGS[WORD_TO_NUM[word]]

def toEnglish(embed, nearest_k = 1):
    return nearest(embed, nearest_k, skipFirst = False)[0]

# A is to B as C is to what ? this function returns the answer for this
def Extrapolate(A, B, C):    
    # calculate C - A + B
    diff = normalize(toEmbedding(A) - toEmbedding(B))
    return toEnglish(normalize(toEmbedding(C) - diff))

# this scores the belong together ness of the given collection of ifc names belong together
def coherence(words):
    embeds = []
    for word in words:
        embeds.append(toEmbedding(word))
    
    embeds = np.array(embeds)
    cosineDist = np.matmul(embeds, np.transpose(embeds))
    flat = np.reshape(cosineDist, [-1, 1])
    print(flat.shape)
    for val in flat:
        if val == 1: continue
        

# the main program starts here
# MEAN_COHERENCE = coherence(WORDS)
# print("mean coherence: %s"%MEAN_COHERENCE)
# # print(WORDS[min1], WORDS[min2])
# print(coherence(["IfcWallStandardCase", "IfcGrid"]))
# print(coherence(["IfcWall", "IfcDoor"]))
if __name__ == "__main__":
    print(nearestToWord("ifcwall",5))
    print(Extrapolate("ifcslab", "ifcwall", "ifcstair"))