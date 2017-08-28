#!/usr/bin/env python

import sys
import frameinstance
import frameinstancesimilarity
from optparse import OptionParser
import logging as log

# log configuration
log.basicConfig(level=log.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s')

# command line argument partsing
parser = OptionParser()
parser.add_option('-i',
                  '--input1',
                  dest="input_file1",
                  help="read triples of the first document from FILE1",
                  metavar="FILE1")
parser.add_option('-j',
                  '--input2',
                  dest="input_file2",
                  help="read triples of the first document from FILE2",
                  metavar="FILE2")
parser.add_option('-l',
                  '--file-list',
                  dest="file_list",
                  help="read pairs of documents from tab-separated file FILELIST",
                  metavar="FILELIST")
parser.add_option('-a',
                  '--alpha',
                  dest="alpha",
                  help="alpha parameter for the frame instance similarity measure")
parser.add_option('-r',
                  '--roles',
                  dest="roles",
                  help="alpha parameter for the frame instance similarity measure")
parser.add_option('-t',
                  '--ftsim',
                  dest="ftsim",
                  help="method for computing the frame type relatedness (occ|dist)")
parser.add_option('-e',
                  '--fesim',
                  dest="fesim",
                  help="method for computing the frame element relatedness (occ|dist)")
parser.add_option('-g',
                  '--aggregate',
                  dest="aggregate",
                  help="aggregation function for computing the document relatedness (avg|max)")

(options, args) = parser.parse_args()

if options.file_list:
    with open(options.file_list) as f:
        document_pairs = [line.rstrip().split('\t') for line in f.readlines()]
elif options.input_file1 and options.input_file2:
    document_pairs = [[options.input_file1, options.input_file2]]
else:
    log.error("You must specify either a pair of input files or a file containing a list of triples file pairs.")
    sys.exit(1)

if options.alpha:
    alpha = eval(options.alpha)
else:
    alpha = 0.5

roles = (options.roles != None and options.roles == 'true')

if options.ftsim:
    ftsim = options.ftsim
else:
    ftsim = 'occ'

if options.fesim:
    fesim = options.fesim
else:
    fesim = 'wup'

if options.aggregate:
    aggregate = options.aggregate
else:
    aggregate = 'avg'

for document_pair in document_pairs:
    log.info('computing similarity between documents {0}, {1} (alpha={2}, roles={3}, ftsim={4}, fesim={5}, agg={6})'.format(document_pair[0], document_pair[1], alpha, roles, ftsim, fesim, aggregate))
    document1 = frameinstance.read_instances_from_nt(document_pair[0])
    document2 = frameinstance.read_instances_from_nt(document_pair[1])

    sims = []
    for fid1, frameinstance1 in document1.iteritems():
        max_sim = -1.0
        for fid2, frameinstance2 in document2.iteritems():
            sim = frameinstancesimilarity.frame_instance_similarity(frameinstance1, frameinstance2, alpha=alpha, roles=roles, ftsim=ftsim, fesim=fesim)
            if sim > max_sim:
                max_sim = sim
        sims.append(max_sim)

    if len(sims)> 0:
        if aggregate == 'avg':
            agg_sim1 = sum(sims)/float(len(sims))
        elif aggregate == 'max':
            agg_sim1 = max(sims)
    else:
        agg_sim1 = 0.0

    sims = []
    for fid2, frameinstance2 in document2.iteritems():
        max_sim = -1.0
        for fid1, frameinstance1 in document1.iteritems():
            sim = frameinstancesimilarity.frame_instance_similarity(frameinstance1, frameinstance2, alpha=alpha, roles=roles, ftsim=ftsim, fesim=fesim)
            if sim > max_sim:
                max_sim = sim
        sims.append(max_sim)

    if len(sims)> 0:
        if aggregate == 'avg':
            agg_sim2 = sum(sims)/float(len(sims))
        elif aggregate == 'max':
            agg_sim2 = max(sims)
    else:
        agg_sim2 = 0.0

    agg_sim = (agg_sim1 + agg_sim2) / 2.0
    print agg_sim
