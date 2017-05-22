#!/usr/bin/env python
import simplejson as json
import sys
from itertools import combinations

sys.stderr.write('importing Wordnet modules...\n')

from nltk.corpus import wordnet as wn

sys.stderr.write('loading WordNet 3.0-3.01 map...\n')

with open("map/JSON_wn31-30.json") as fp:
    wn31_30 = json.load(fp)

def offset31synset(offset_31):
    offset_30 = wn31_30[offset_31]
    return wn._synset_from_pos_and_offset(str(offset_30[-1:]), int(offset_30[:8]))

def similarity(offset_1, offset_2):
    return wn.wup_similarity(offset31synset(offset_1), offset31synset(offset_2))

sys.stderr.write('reading synset offset list...\n')

with open(sys.argv[1]) as fp:
    offsets = [line.rstrip() for line in fp]
n_pairs = (len(offsets)*(len(offsets)+1))/2

sys.stderr.write('computing similarities...\n')

n = 0
for offset_1, offset_2 in combinations(offsets, 2):
    sim = similarity(offset_1, offset_2)
    if sim:
        print sim, offset_1, offset_2
    n += 1
    if n % 1000 == 0:
        progress = (float(n)/float(n_pairs))*100.0
        sys.stderr.write('{0:.2f}%\t({1}/{2})\r'.format(progress, n, n_pairs))
