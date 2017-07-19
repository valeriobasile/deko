#!/usr/bin/env python

from random import random
from nltk.corpus import framenet as fn
import math

# read the lexical units dictionary
lexical_units = dict()
with open("../resources/frame_lexical_units.tsv") as f:
    for line in f:
        frame, lu = line.rstrip().split('\t')
        if not frame in lexical_units:
            lexical_units[frame] = []
        lexical_units[frame].append(lu)

# read Semcor lemmas:
semcor_lemmas = dict()
semcor_sentences = dict()
with open("../resources/semcor3.0_lemmas.tsv") as f:
    for line in f:
        sentence_id, lemma = line.rstrip().split('\t')

        if not sentence_id in semcor_lemmas:
            semcor_lemmas[sentence_id] = []
        semcor_lemmas[sentence_id].append(lemma)

        if not lemma in semcor_sentences:
            semcor_sentences[lemma] = []
        semcor_sentences[lemma].append(sentence_id)

def frame_relatedness(frame1, frame2):
    lus1 = lexical_units[frame1]
    lus2 = lexical_units[frame2]

    cf1 = set()
    for lu in lus1:
        if lu in semcor_sentences:
            cf1 = cf1.union(set(semcor_sentences[lu]))

    cf2 = set()
    for lu in lus2:
        if lu in semcor_sentences:
            cf2 = cf2.union(set(semcor_sentences[lu]))

    l1 = float(len(cf1))/36405.0
    l2 = float(len(cf2))/36405.0
    l12 = float(len(cf1.intersection(cf2)))/36405.0
    #print l1, l2, l12
    if l12 == 0.0 or l1 == 0.0 or l2 == 0.0:
        return 0.0
    else:
        return math.log(l12/(l1*l2), 2.0)

def frame_element_relatedness(fe1, fe2):
    return 0.0

def frame_instance_similarity(fi1, fi2):
    # the alpha prameter will be read from a config file
    alpha = 1.0
    frame_sim = frame_relatedness(fi1.frame_type, fi2.frame_type)
    fe_sim = frame_element_relatedness(fi1.frame_elements, fi2.frame_elements)
    sim = alpha * frame_sim + (1.0-alpha) * fe_sim
    return sim
