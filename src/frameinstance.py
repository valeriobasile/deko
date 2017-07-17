#!/usr/bin/env python
import logging as logging

def entity_basename(entity):
    return entity[1:-1].split('/')[-1]

class FrameElement:
    def __init__(self):
        self.role = None
        self.entity = None

    def __str__(self):
        return "{0}: {1}".format(self.role, self.entity)

class FrameInstance:
    def __init__(self, _id):
        self.id = _id
        self.frame_type = None
        self.frame_elements = []

    def __str__(self):
        #frame_elements = ''
        #for fe in self.frame_elements:
        #    frame_elements += "\n{0}".format(str(fe))

        return """Frame Instance: {0}
Frame type: {1}
Frame elements ({2}):
{3}""".format(self.id,
              self.frame_type,
              len(self.frame_elements),
              "\n".join(["\t{0}".format(str(fe)) for fe in self.frame_elements]))

def read_instances_from_nt(frame_instance_file):
    frame_instances = dict()
    with open(frame_instance_file) as f:
        for line in f:
            # n-triple parsing
            s, p, o, _ = line.rstrip().split(' ')
            frame_id = entity_basename(s).split('_')[-1]
            if not frame_id in frame_instances:
                fi = FrameInstance(frame_id)
                frame_instances[frame_id] = fi

            if p == '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>':
                frame_instances[frame_id].frame_type = entity_basename(o).replace('frame-', '')
            else:
                role = entity_basename(p).replace('fe-', '')
                fe = FrameElement()
                fe.role = role
                fe.entity = o
                frame_instances[frame_id].frame_elements.append(fe)
    return frame_instances
