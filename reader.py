from ops import *

# convert a character to ascii code (8 bits)
def prepareChar(ch):
    if len(ch) != 1:
        raise ValueError("Please supply a single character for the ascii lookup")
    binStr = "{0:08b}".format(ord(ch))
    binList = []
    for d in binStr:
        binList.append(int(d))
    
    return binList