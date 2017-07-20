#!/usr/bin/env python

from random import random
from nltk.corpus import framenet as fn
from nltk.corpus import wordnet
import math
import os
import logging as log

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

# read Semcor lemmas:
log.info("reading Semcor 3.0 lemmas")
semcor_lemmas = dict()
semcor_sentences = dict()
with open("../resources/semcor3.0_lemmas.tsv") as f:
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
with open("../resources/wordnet_offsets.tsv") as f:
    for line in f:
        offset, name = line.rstrip().split('\t')
        offset2name[offset] = name
        name2offset[name] = offset

def frame_relatedness(frame1, frame2):
    """Compute the relatedness between two frame types, using one of the
    methods proposed by Pennacchiotti and Wirth (ACL 2009)."""
    return cr_occ(frame1, frame2)

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

def synset_similarity(s1, s2):
    """Input: two WordNet 3.0 synset identifier, e.g, '06326797-n'
    Output: a real number between 0.0 and 1.0"""
    return wup_similarity(s1, s2)

def frame_element_relatedness(fe1, fe2, roles=False):
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
                synsetid1 = wn31wn30[s1.entity[1:-1].split('/')[-1]]
                synsetid2 = wn31wn30[s2.entity[1:-1].split('/')[-1]]
                sim = synset_similarity(synsetid1, synsetid2)
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
                synsetid1 = wn31wn30[s1.entity[1:-1].split('/')[-1]]
                synsetid2 = wn31wn30[s2.entity[1:-1].split('/')[-1]]
                sim = synset_similarity(synsetid1, synsetid2)
            if sim > max_sim:
                max_sim = sim
        sims2.append(max_sim)

    if len(sims2) > 0:
        sim2 = sum(sims2)/float(len(sims2))
    else:
        sim2 = 0.0

    return (sim1+sim2)/2.0

def frame_instance_similarity(fi1, fi2, alpha=0.5, roles=False):
    # the alpha prameter will be read from a config file
    frame_sim = frame_relatedness(fi1.frame_type, fi2.frame_type)
    fe_sim = frame_element_relatedness(fi1.frame_elements, fi2.frame_elements, roles=roles)
    sim = alpha * frame_sim + (1.0-alpha) * fe_sim
    return sim
