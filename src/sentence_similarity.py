#!/usr/bin/env python

import sys
import frameinstance
import frameinstancesimilarity

document1 = frameinstance.read_instances_from_nt(sys.argv[1])
document2 = frameinstance.read_instances_from_nt(sys.argv[2])

sims = []
for fid1, frameinstance1 in document1.iteritems():
    max_sim = -1.0
    for fid2, frameinstance2 in document2.iteritems():
        sim = frameinstancesimilarity.frame_instance_similarity(frameinstance1, frameinstance2)
        if sim > max_sim:
            max_sim = sim
    sims.append(max_sim)

if len(sims)> 0:
    avg_sim1 = sum(sims)/float(len(sims))
else:
    avg_sim1 = 0.0

sims = []
for fid2, frameinstance2 in document2.iteritems():
    max_sim = -1.0
    for fid1, frameinstance1 in document1.iteritems():
        sim = frameinstancesimilarity.frame_instance_similarity(frameinstance1, frameinstance2)
        if sim > max_sim:
            max_sim = sim
    sims.append(max_sim)

if len(sims)> 0:
    avg_sim2 = sum(sims)/float(len(sims))
else:
    avg_sim2 = 0.0

avg_sim = (avg_sim1 + avg_sim2) / 2.0
print avg_sim
