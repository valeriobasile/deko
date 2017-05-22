#!/usr/bin/env python
from optparse import OptionParser
import os
import logging as log
import sys
import operator
from math import floor

# transforms a list of lists into a flat list
def flatten(l):
    return [item for sublist in l for item in sublist]

# transforms a list with repetitions into a dictionary of element frequency
def counts(l):
    return {i:l.count(i) for i in l}

# transform a count dictionary into a list of tuples ordered by counts
def ordered_counts(l):
    return sorted(counts(l).items(), key=operator.itemgetter(1), reverse=True)

def show_color(i, n):
    intensity = 0.5 - ((float(i)/float(n))/2.0)
    return 'rgb({0}, {0}, {0})'.format(int(floor(intensity*255)))

# log configuration
log.basicConfig(level=log.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s')

parser = OptionParser()
parser.add_option('-c',
                  '--clusters',
                  dest="cluster_file",
                  help="read clusters from FILE",
                  metavar="FILE")
parser.add_option('-i',
                  '--instance-dir',
                  dest="instance_file",
                  help="read frame instances from FILE",
                  metavar="FILE")
parser.add_option('-m',
                  '--mappings',
                  dest="mapping_dir",
                  default='/home/vbasile/dev/learningbyreading/resources',
                  help="read synset mappings from DIRECTORY",
                  metavar="DIRECTORY")

(options, args) = parser.parse_args()
if not options.cluster_file or not options.instance_file:
    log.error('please specify both clusters file and instances file, exiting')
    sys.exit(1)

log.info('reading mapping files from {0}'.format(options.mapping_dir))

# builds a dictionary of frame names indexed by wordnet synset id
offset2bn = dict()
bn2offset = dict()
offset2wn = dict()
wn2offset = dict()
wn2bn = dict()
bn2wn = dict()
bn2dbpedia = dict()
dbpedia2bn = dict()

# the mapping is in a tabular file, e.g.:
# s00069798n Scout-n#2-n 110582611-n
with open(os.path.join(options.mapping_dir, 'bn35-wn31.map')) as f:
    for line in f:
        bn_id, wn_id, wn_offset = line.rstrip().split(' ')
        offset2bn[wn_offset[1:]] = bn_id
        bn2offset[bn_id] = wn_offset[1:]
        offset2wn[wn_offset[1:]] = wn_id
        wn2offset[wn_id] = wn_offset[1:]
        wn2bn[wn_id] = bn_id
        bn2wn[bn_id] = wn_id

# Mapping BabelNet-DBpedia
# s00000006n Dodecanol
with open(os.path.join(options.mapping_dir, 'bn-dbpedia')) as f:
    for line in f:
        bn_id, dbpedia_id = line.rstrip().split(' ')
        dbpedia2bn[dbpedia_id] = bn_id
        bn2dbpedia[bn_id] = dbpedia_id

log.info('reading clusters from file {0}'.format(options.cluster_file))
clusters = dict()
with open(options.cluster_file) as f:
    for line in f:
        if not "sense" in line: # there is a bug in one of the frame type names
            instance_id, cluster_id = line.rstrip().split(' ')
            if not cluster_id in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(instance_id.split('_')[-1])

log.info('reading instances from file {0}'.format(options.instance_file))
instance_types = dict()
instance_elements = dict()
with open(options.instance_file) as f:
    for line in f:
        s, p, o, _ = line.rstrip().split(' ')
        instance_id = s.split('_')[-1][:-1]
        # frame types
        if p == '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>':
            instance_type_fn = o.split('/')[-1][:-1].split('-')[1]
            instance_types[instance_id] = instance_type_fn
        # frame elements
        else:
            role = '-'.join(p.split('/')[-1][:-1].split('-')[1:])
            element_type_offset = o.split('/')[-1][:-1]
            element_type_bn = offset2bn.get(element_type_offset, None)
            element_type_wn = offset2wn.get(element_type_offset, None)
            element_type_dbp = bn2dbpedia.get(element_type_bn, None)
            filled_role = (role, element_type_wn)
            if not filled_role in instance_elements:
                instance_elements[instance_id] = []
            instance_elements[instance_id].append(filled_role)


# sort clusters by size
clusters_sorted = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
for cluster_id, instances in clusters_sorted:
    cluster_instance_types = [instance_types[instance_id] for instance_id in instances]
    cluster_instance_types_count = ordered_counts(cluster_instance_types)
    cluster_elements_roles = [instance_elements[instance_id] for instance_id in instances]
    cluster_elements = [x[1] for x in flatten(cluster_elements_roles)]
    cluster_elements_roles = flatten(cluster_elements_roles)
    cluster_elements_roles_count = ordered_counts(cluster_elements_roles)
    cluster_elements_count = ordered_counts(cluster_elements)

    if cluster_instance_types_count[0][1] > 1 and cluster_elements_roles_count[0][1] > 1:
        frame_type = cluster_instance_types_count[0][0]
        role = cluster_elements_roles_count[0][0][0]
        try:
            frame_element = wn2offset[cluster_elements_roles_count[0][0][1]]
        except:
            log.error('synset lost in mapping: {0}'.format(cluster_elements_roles_count[0][0][1]))
            continue
        print "<http://framebase.org/ns/frame-{0}> <http://framebase.org/ns/fe-{1}> <http://wordnet-rdf.princeton.edu/wn31/{2}>.".format(frame_type, role, frame_element)
