from ops import *
from model_embeddings import getAllWords
import math

embeddings = loadFromFile("savedEmbeddings/embeddings.pkl")
WORDS, wordToNum = getAllWords()


def normalize(vector):
    norm = np.sqrt(np.square(vector).sum())
    if norm == 0:
        return vector
    else:
        return vector/norm

def nearest(testEmbedding,numNearest = 1, skipFirst = True):
    similarity = np.matmul(testEmbedding, np.transpose(embeddings))
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
    return embeddings[wordToNum[word]]

def toEnglish(embed):
    return nearest(embed,1, skipFirst = False)[0]

# extrapolates
def Extrapolate(A, B, C):    
    # calculate C - A + B
    return toEnglish(toEmbedding(C) - toEmbedding(A) + toEmbedding(B))

# this scores the belong together ness of the given collection of ifc names belong together
def coherence(words):
    embeds = []
    maxScore = -math.inf
    for word in words:
        compat = []
        for word2 in words:
            if word == word2: continue
            compat.append(toEmbedding(word2))
        
        compat = np.array(compat)
        wordEmbed = np.array([toEmbedding(word)])
        score = np.matmul(wordEmbed, np.transpose(compat)).mean()
        if score > maxScore:
            maxScore = score
        embeds.append(score)
    
    print("max score: %s"%maxScore)
    return np.array(embeds).mean()

# the main program starts here
MEAN_COHERENCE = coherence(WORDS)
print("mean coherence: %s"%MEAN_COHERENCE)
# print(WORDS[min1], WORDS[min2])
print(coherence(["IfcWallStandardCase", "IfcGrid"]))
# print(coherence(["IfcWall", "IfcDoor"]))

# print(nearestToWord("IfcWallStandardCase",45))