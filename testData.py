from ops import *

words = dataset("data/")
batch = words.next_batch(5)

for i in range(5):
    print("%s - %s"%(batch[0][i], batch[1][i]))

print("============================")

batch = words.next_batch(10)
for i in range(10):
    print("%s - %s"%(batch[0][i], batch[1][i]))