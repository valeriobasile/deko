#!/usr/bin/env python


import logging as log
import gensim

# log configuration
log.basicConfig(level=log.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s')

# read the lexical units dictionary
log.info("reading FrameNet lexical units")
lexical_units = dict()
with open("../resources/frame_lexical_units.tsv") as f:
    for line in f:
        frame, lu = line.rstrip().split('\t')
        if not frame in lexical_units:
            lexical_units[frame] = []
        lexical_units[frame].append(lu)

'''
# loading word2vec vector model
log.info("loading GoogleNews negative 300 word2vec binary model")
model = gensim.models.KeyedVectors.load_word2vec_format('/home/vbasile/Downloads/GoogleNews-vectors-negative300.bin', binary=True)
'''

def read_vector_file(vector_file):
    f = open(vector_file,'r')
    model = {}
    for line in f:
        splitLine = line.split()
        word = splitLine[0]
        embedding = [float(val) for val in splitLine[1:]]
        model[word] = embedding
    return model

log.info("loading GloVe 300 model")
model = read_vector_file('/home/vbasile/Downloads/glove.6B.300d.txt')
log.info("Done. {0} words loaded".format(len(model)))

for frame, lus in lexical_units.iteritems():
    vector = [0.0 for dim in range(300)]
    n = 0.0
    for lu in lus:
        if lu in model:
            vector = [vector[dim]+value for dim, value in enumerate(model[lu])]
            n += 1.0
    if n > 0.0:
        vector = [value/n for dim, value in enumerate(vector)]
    print frame, ' '.join([str(i) for i in vector])
