from ops import *

def getAllWords():
    with open('data/vocabulary.dat') as f:
        words = f.read().splitlines()
    wordList = list(words)
    wordDict = dict()
    for i in range(len(words)):
        wordDict[wordList[i]] = i 
    return [wordList, wordDict]