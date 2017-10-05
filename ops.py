import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import tensorflow as tf
import numpy as np
import os
import pickle
import time
from PIL import Image

# some global params
batch_size = 600
# the directory to which teh results will be saved
resDir = 'results/'
# folder to log the training progress in
LOG_DIR = "train_log/"

# learning_rate = 1.0
learning_rate = 0.0001

model_save_path = 'savedEmbeddings/rnn_reader.ckpt'

# this method saves the model
def saveModel(sess, savePath = model_save_path):
    print('\n...saving the models, please wait...')
    saver = tf.train.Saver()
    saver.save(sess, savePath)
    print('Saved the model to %s'%savePath)

# this method loads the saved model
def loadModel(sess, savedPath = model_save_path):
    print('\n...loading the models, please wait...')
    saver = tf.train.Saver()
    saver.restore(sess, savedPath)
    print('Loaded the model from %s'%savedPath)

# weight variable
def weightVariable(shape, name):
    initializer = tf.truncated_normal_initializer(mean=0.0, stddev=0.02)
    weight = tf.get_variable(name=name, shape=shape, initializer=initializer)
    return weight

# bias variable
def biasVariable(shape, name):
    initializer = tf.constant_initializer(0.01)
    bias = tf.get_variable(name=name, shape=shape, initializer=initializer)
    return bias

# 2d convolutional layer
def conv2d(x, W, strides = [1,2,2,1]):
    return tf.nn.conv2d(x, W, strides=strides, padding='SAME')

# 3d convolutional layer
def conv3d(x, W, strides = [1,2,2,1,1]):
    return tf.nn.conv3d(x,W,strides = strides, padding='SAME')

# deconv layer
def deConv3d(y, w, outShape, strides=[1,2,2,2,1]):
    return tf.nn.conv3d_transpose(y, w, output_shape = outShape, strides=strides, padding='SAME')

# this is max-pooling for 3d convolutional layers
def max_pool2x2x1(x):
    return tf.nn.max_pool3d(x,ksize=[1,2,2,1,1],strides=[1,2,2,1,1],padding='SAME')

# this is a 2x2 max-pooling layer for 2d convolutional layers
def max_pool2x2(x):
    return tf.nn.max_pool(x,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')

# converts data to image
def toImage(data):
    data = np.reshape(data, [48,64])
    newData = 255*data
    # converting new data into integer format to make it possible to export it as a bitmap
    # in this case converting it into 8 bit integer
    newData = newData.astype(np.uint8)
    return Image.fromarray(newData)

# this method converts a list of images into a feed ready batch
def prepareImages(imageList, normalize = True):
    batch = []
    for img in imageList:
        arr = prepareImage(img, normalize=normalize)
        batch.append(arr)
    return batch

# this one prepares a single image and returns it as an array
def prepareImage(img, normalize = True):
    arr = np.array(img)
    arr = arr.astype(np.float32)
    if normalize:
        arr /= 255

    return arr

# this method returns the time estimate as a string
def estimate_time(startTime, totalCycles, finishedCycles):
    timePast = time.time() - startTime
    if timePast < 10:
        return '...calculating...'
    cps = finishedCycles/timePast
    if cps == 0:
        return '...calculating...'
        
    secsLeft = (totalCycles - finishedCycles)/cps

    # double slash is an integer division, returns the quotient without the decimal
    hrs, secs = secsLeft//3600, secsLeft % 3600
    mins, secs = secs//60, secs % 60

    timeStr = '%.0fh%.0fm%.0fs remaining'%(hrs, mins, secs) + ' '*10
    return timeStr

# this is the dataset object which is responsible with supplying data for training as well as
# testing purposes
class dataset:
    # the dirPath is the path of the directory
    def __init__(self, dirPath = './'):
        self.dirPath = dirPath
        # getting the list of files in the dirPath
        self.trainFileList = os.listdir(self.dirPath)
        # removing the vocab file from the list
        if len(self.trainFileList) > 1:
            self.trainFileList.remove("vocabulary.dat")

        #removing any other file with the wrong extension
        i = 0
        while i < len(self.trainFileList):
            if not self.trainFileList[i].endswith('.dat'):
                # print('removing %s'%self.trainFileList[i])
                del self.trainFileList[i]
                i -= 1
            
            i += 1
        
        # print(self.trainFileList)
        
        self.curFile = None
        if len(self.trainFileList) > 0:
            self.curFile = self.trainFileList[0]
        self.data = None
        self.load_data()

        # this is the number of data samples currently loaded
        self.data_num = self.data[0].shape[0]

        # this is the counter for where we are reading the data in the currently loaded set
        self.c = 0
    
    # returns the name of the next file to be used once the current file is exhausted
    def next_file(self):
        fileNum = self.trainFileList.index(self.curFile)
        fileNum = (fileNum + 1)%len(self.trainFileList)
        nextFile = self.trainFileList[fileNum]
        return nextFile
    
    # this loads the data from the current file into the self.data
    def load_data(self, silent = False):
        with open(self.dirPath + self.curFile) as inp:
            if not silent: print('Loading data from %s...'%self.curFile)
            lines = inp.read().splitlines()
        
        labels = []
        targets = []
        for line in lines:
            if line == "": continue
            label, target = line.split(" ")
            labels.append(label)
            targets.append(target)
        dSet = [labels, targets]
        
        # self.data = [np.expand_dims(np.array(dSet[0]),3), np.array(dSet[1])]
        # print(type(dSet).__name__)
        self.data = [np.array(dSet[0]), np.expand_dims(np.array(dSet[1]),1)]
        self.data_num = self.data[0].shape[0]
        # self.data = dSet
        # if not silent: print('Dataset in %s is successfully loaded'%self.dirPath)
    
    # this returns the next batch of the size - size
    def next_batch(self, size):
        if self.c + size >= self.data_num:
            end = self.data_num
            dataNeeded = self.c + size - self.data_num

            batch1 = [self.data[0][self.c: end], self.data[1][self.c: end]]

            # now getting the remaining data from the next file
            self.c = 0
            self.curFile = self.next_file()
            # self.load_data(silent = True)
            self.load_data()

            batch2 = self.next_batch(dataNeeded)
            # now joining batch 2 to the original batch
            batch = [np.concatenate((batch1[0], batch2[0]), axis=0), np.concatenate((batch1[1], batch2[1]), axis=0)]

        elif self.c + size < self.data_num:
            end = self.c + size
            
            batch = [self.data[0][self.c: end], self.data[1][self.c: end]]
            self.c = end

        return batch

# this just saves any given data to any given path
def writeToFile(data, path):
    with open(path, 'wb') as output:
        pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)
    
def loadFromFile(path):
    with open(path, "rb") as f:
        return pickle.load(f)

# this creates summaries for variables to be used by tensorboard
def summarize(varT):
    varName = varT.name[:-2]
    with tf.name_scope(varName):
        var_mean = tf.reduce_mean(varT)
        var_sum = tf.reduce_sum(varT)
        tf.summary.scalar('mean', var_mean)
        tf.summary.scalar('sum', var_sum)

        with tf.name_scope('stddev'):
            stddev = tf.sqrt(tf.reduce_mean(tf.square(varT - var_mean)))
        
        tf.summary.scalar('stddev', stddev)
        tf.summary.scalar('max', tf.reduce_max(varT))
        tf.summary.scalar('min', tf.reduce_min(varT))
        tf.summary.histogram('histogram', varT)

# this returns the writer objects for training and testing
def getSummaryWriters(sess):
    train_writer = tf.summary.FileWriter(log_dir + 'train', sess.graph)
    test_writer = tf.summary.FileWriter(log_dir + 'test')

    return [train_writer, test_writer]


# from here down is the sandbox place to check and verify the code above before using it in
# the other files
