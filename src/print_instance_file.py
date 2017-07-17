#!/usr/bin/env python

import sys
import frameinstance

frameinstances = frameinstance.read_instances_from_nt(sys.argv[1])
for fid, frameinstance in frameinstances.iteritems():
    print frameinstance
