# -*- coding: utf-8 -*

import re
import os
import json
from datetime import datetime
from os.path import join
from frameinstance import FrameElement, FrameInstance

def read_dataset(all_instances_path, repeated_instances_path=None, delete_repetition=True):
    frame_instances = {}
    index_instances = {}

    for dir_path, dir_names, file_names in os.walk(all_instances_path):
        for file_name in [f for f in file_names if f.endswith(".nt")]:
            file_path = os.path.join(dir_path, file_name)
            read_frame_instances(file_path, frame_instances, index_instances, delete_repetition)

    if repeated_instances_path:
        with open(repeated_instances_path, "w") as fout:
            json.dump(index_instances, fout, indent=4, sort_keys=True)

    return frame_instances

def read_frame_instances(file_path, frame_instances, index_instances, delete_repetition):
    previous_instance_id = None

    with open(file_path, "r") as fin:
        for line in fin:
            tuple_elements = line.split(" ")
            instance_id = re.match("<http://framebase.org/ns/fi-(.+)>", tuple_elements[0]).group(1)

            if instance_id != previous_instance_id:
                fi = FrameInstance(instance_id)
                fi.frame_type = re.match("<http://framebase.org/ns/frame-(.+)>", tuple_elements[2]).group(1)
                frame_instances[instance_id] = fi
                if previous_instance_id:
                    check_repetition(previous_instance_id, frame_instances, index_instances, delete_repetition)       
                previous_instance_id = instance_id
            else:
                fe = FrameElement()
                fe.role = re.match("<http://framebase.org/ns/fe-(.+)>", tuple_elements[1]).group(1)
                fe.entity = tuple_elements[2]
                frame_instances[instance_id].frame_elements.append((fe))

    if previous_instance_id:
        check_repetition(instance_id, frame_instances, index_instances, delete_repetition)

def check_repetition(instance_id, frame_instances, index_instances, delete_repetition):
    index = create_index(frame_instances[instance_id])
    if index in index_instances:
        index_instances[index].append(instance_id)
        if delete_repetition:
            del frame_instances[instance_id]
    else:
        index_instances[index] = [instance_id]

def create_index(frame_instance):
    frame_type = frame_instance.frame_type
    frame_elements = sorted([x.entity.split('/')[-1][:-1] for x in frame_instance.frame_elements])
    frame_index = frame_type + "#" + "#".join(frame_elements)

    return frame_index