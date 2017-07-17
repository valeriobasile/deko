#!/usr/bin/env python
import logging as logging

class FrameElement:
    def __init__(self):
        self.role = None
        self.entity = None

class FrameInstance:
    def __init__(self, _id):
        self.id = _id
        self.frame_type = None
        self.frame_elements = []

def read_instances_from_nt(frame_instance_file):
    frame_instances = dict()
    with open(frame_instance_file) as f:
        for line in f:
            # n-triple parsing
            s, p, o, _ = line.rstrip().split(' ')
            if not s in frame_instances:
                frame_type, frame_id = s[1:-1].split('/')[-1].replace('fi-', '').split('_')
                fi = FrameInstance(frame_id)
                fi.frame_type = frame_type
                frame_instances[frame_id] = fi
    return frame_instances
