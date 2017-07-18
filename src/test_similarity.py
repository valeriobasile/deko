#!/usr/bin/env python

import sys
import frameinstance
import frameinstancesimilarity

document1 = frameinstance.read_instances_from_nt(sys.argv[1])
document2 = frameinstance.read_instances_from_nt(sys.argv[2])
for fid1, frameinstance1 in document1.iteritems():
    for fid2, frameinstance2 in document2.iteritems():
        print fid1, fid2, frameinstancesimilarity.frame_instance_similarity(frameinstance1, frameinstance2)
