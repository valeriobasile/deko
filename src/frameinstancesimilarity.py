#!/usr/bin/env python

from random import random
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet
import math
import os
import logging as log
import gensim
from scipy.spatial.distance import cosine
import MySQLdb

# log configuration
log.basicConfig(level=log.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s')

# read the lexical units dictionary
log.info("reading FrameNet lexical units")
lexical_units = dict()
with open(os.path.join(os.path.dirname(__file__), "../resources/frame_lexical_units.tsv")) as f:
    for line in f:
        frame, lu = line.rstrip().split('\t')
        if not frame in lexical_units:
            lexical_units[frame] = []
        lexical_units[frame].append(lu)

# read Semcor lemmas:
log.info("reading Semcor 3.0 lemmas")
semcor_lemmas = dict()
semcor_sentences = dict()
with open(os.path.join(os.path.dirname(__file__), "../resources/semcor3.0_lemmas.tsv")) as f:
    for line in f:
        sentence_id, lemma, sense = line.rstrip().split('\t')

        if not sentence_id in semcor_lemmas:
            semcor_lemmas[sentence_id] = []
        semcor_lemmas[sentence_id].append(lemma)

        if not lemma in semcor_sentences:
            semcor_sentences[lemma] = []
        semcor_sentences[lemma].append(sentence_id)

# Mapping different WN versions
log.info("reading WordNet 3.0-3.1 mapping")
wn30wn31 = dict()
wn31wn30 = dict()
with open(os.path.join(os.path.dirname(__file__), '../resources/wn30-31')) as f:
    for line in f:
        wn30, wn31 = line.rstrip().split(' ')
        wn30wn31[wn30] = wn31
        wn31wn30[wn31] = wn30

# creating dictionary of Wordnet synset id (offsets)
log.info("reading WordNet 3.0 offset-id mapping")
offset2name = dict()
name2offset = dict()
with open(os.path.join(os.path.dirname(__file__), "../resources/wordnet_offsets.tsv")) as f:
    for line in f:
        offset, name = line.rstrip().split('\t')
        offset2name[offset] = name
        name2offset[name] = offset

# open connection to the DB
db = MySQLdb.connect(host="127.0.0.1",    # your host, usually localhost
                     user="nasari",         # your username
                     passwd="nasari",  # your password
                     db="nasari")        # name of the data base
cur = db.cursor()

def read_vector_file(vector_file):
    f = open(vector_file,'r')
    model = {}
    for line in f:
        splitLine = line.split()
        word = splitLine[0]
        embedding = [float(val) for val in splitLine[1:]]
        model[word] = embedding
    return model

log.info("loading frame vectors")
frame_vectors = read_vector_file(os.path.join(os.path.dirname(__file__), '../resources/frame_vectors_glove6b.txt'))

def nasari_similarity(e1, e2):
    if e1 == e2:
        return 1.0
    bnid1 = "bn:{0}".format(e1[1:])
    bnid2 = "bn:{0}".format(e2[1:])
    sql = "select * from vector where babelnetid = '{0}' or babelnetid = '{1}';".format(db.escape_string(bnid1), db.escape_string(bnid2))
    cur.execute(sql)
    rows = cur.fetchall()
    # check that there are two rows
    if len(rows) != 2:
        return -1.0
    return (1.0-cosine(rows[0][2:], rows[1][2:]))

def frame_relatedness(frame1, frame2, ftsim='occ'):
    """Compute the relatedness between two frame types, using one of the
    methods proposed by Pennacchiotti and Wirth (ACL 2009)."""
    if ftsim == 'occ':
        return cr_occ(frame1, frame2)
    elif ftsim == 'dist':
        return ftsim_dist(frame1, frame2)

def ftsim_dist(frame1, frame2):
    v1 = frame_vectors[frame1]
    v2 = frame_vectors[frame2]
    return 1.0 - cosine(v1, v2)

def cr_occ(frame1, frame2):
    """This is an implementation of the first co-occurrence measure of
    Pennacchiotti and Wirth (ACL2009), described in Sec. 4.2.1 of the paper.
    Input: two frame type names, e.g., Commerce_buy/Commerce_sell.
    Output: a real number (Pointwise-mutual information)."""

    lus1 = lexical_units[frame1]
    lus2 = lexical_units[frame2]

    '''Set of the contexts (sentences in Semcor 3.0) where the lexical units
    of frame1 occur'''
    cf1 = set()
    for lu in lus1:
        if lu in semcor_sentences:
            cf1 = cf1.union(set(semcor_sentences[lu]))

    '''Set the contexts (sentences in Semcor 3.0) where the lexical units
    of frame2 occur'''
    cf2 = set()
    for lu in lus2:
        if lu in semcor_sentences:
            cf2 = cf2.union(set(semcor_sentences[lu]))

    '''Set of the contexts where lexical units from both frames co-occur'''
    cf12 = cf1.intersection(cf2)

    '''Compute the Point-wise Mutual Information'''
    l1 = float(len(cf1))/float(len(semcor_lemmas))
    l2 = float(len(cf2))/float(len(semcor_lemmas))
    l12 = float(len(cf12))/float(len(semcor_lemmas))
    #print l1, l2, l12
    if l12 == 0.0 or l1 == 0.0 or l2 == 0.0:
        return 0.0
    else:
        return math.log(l12/(l1*l2), 2.0)

def wup_similarity(s1, s2):
    synset1 = wordnet.synset(offset2name[s1])
    synset2 = wordnet.synset(offset2name[s2])
    return synset1.wup_similarity(synset2)

def synset_similarity(e1, e2, fesim='wup'):
    """Input: two concept URI, e.g, '<http://babelnet.org/rdf/s00046516n>?'
    Output: a real number between 0.0 and 1.0"""

    synsetid1 = e1[1:-1].split('/')[-1]
    synsetid2 = e2[1:-1].split('/')[-1]
    if fesim=='wup':
        return wup_similarity(wn31wn30[synsetid1], wn31wn30[synsetid2])
    elif fesim == 'dist':
        return nasari_similarity(synsetid1, synsetid2)

def frame_element_relatedness(fe1, fe2, roles=False, fesim='wup'):
    """Computes an aggregate measure of relatedness between the entities
    involved in the frame elements.
    Input: two frame elements
    Output: a real number between 0.0 and 1.0"""
    sims1 = []
    for s1 in fe1:
        max_sim = 0.0
        for s2 in fe2:
            if roles == True and s1.role != s2.role:
                sim = 0.0
            else:
                sim = synset_similarity(s1.entity, s2.entity, fesim=fesim)
            if sim > max_sim:
                max_sim = sim
        sims1.append(max_sim)

    if len(sims1) > 0:
        sim1 = sum(sims1)/float(len(sims1))
    else:
        sim1 = 0.0

    sims2 = []
    for s2 in fe2:
        max_sim = 0.0
        for s1 in fe1:
            if roles == True and s1.role != s2.role:
                sim = 0.0
            else:
                sim = synset_similarity(s1.entity, s2.entity, fesim=fesim)
            if sim > max_sim:
                max_sim = sim
        sims2.append(max_sim)

    if len(sims2) > 0:
        sim2 = sum(sims2)/float(len(sims2))
    else:
        sim2 = 0.0

    return (sim1+sim2)/2.0

def frame_instance_similarity(fi1, fi2, alpha=0.5, roles=False, ftsim='occ', fesim='wup'):
    # the alpha prameter will be read from a config file
    frame_sim = frame_relatedness(fi1.frame_type, fi2.frame_type, ftsim=ftsim)
    fe_sim = frame_element_relatedness(fi1.frame_elements, fi2.frame_elements, roles=roles, fesim=fesim)
    sim = alpha * frame_sim + (1.0-alpha) * fe_sim
    return sim
