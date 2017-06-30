#!/usr/bin/env python
import sys
from nltk.corpus import wordnet
import logging as log

class FrameInstance:
    def __init__(self, _frame_instance_id):
        self.frame_instance_id = _frame_instance_id
        self.frame_type = None
        self.frame_elements = []

    def __repr__(self):
        return """Frame Instance: {0}
Frame Type: {1}
Frame Elements:
{2}""".format(
    self.frame_instance_id, 
    self.frame_type, 
    '\n'.join(["{0}: {1}".format(fe_r, fe_f) for fe_r, fe_f in self.frame_elements]))

    def verbalize(self):
        if len(self.frame_elements)>1:
            for role, concept in self.frame_elements:
                wn31id = concept[1:-1].split('/')[-1]
                if wn31id in wn31lemma:
                    print "{0} is the {1} in the frame {2}".format(
                        wn31lemma[wn31id].replace('+', ' '), 
                        role[1:-1].split('-')[-1], 
                        self.frame_type[1:-1].split('-')[-1])

wn31lemma = dict()
with open('../../resources/bn35-wn31.map') as f:
    for line in f:
        bnid, wnlemma, wnoffset = line.rstrip().split(' ')
        lemma = wnlemma.split('#')[0].split('-')[0]
        wn31lemma[wnoffset[1:]] = lemma
        
frame_instances = dict()
with open(sys.argv[1]) as f:
    for line in f:
        try:
            s, p, o, _ = line.rstrip().split(' ')
        except:
            log.error('cannot parse line:\n{0}'.format(line))
        
        frame_instance_id = s[1:-1].replace('http://framebase.org/ns/fi-', '')
        
        # new frame instance
        if p == '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>':
            fi = FrameInstance(frame_instance_id)
            fi.frame_type = o
            frame_instances[frame_instance_id] = fi
        # existing frame instance
        else:
            fe = (p, o)
            frame_instances[frame_instance_id].frame_elements.append(fe)

for frame_instance_id, frame_instance in frame_instances.iteritems():
    frame_instance.verbalize()
    

