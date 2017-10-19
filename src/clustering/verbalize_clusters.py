# -*- coding: utf-8 -*

import json
import logging
from datetime import datetime
from os.path import join, dirname
from reduce_dataset import read_dataset

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')#, filename='clustering.log')

wn31lemma = dict()
with open('../../resources/bn35-wn31.map') as f:
    for line in f:
        bnid, wnlemma, wnoffset = line.rstrip().split(' ')
        lemma = wnlemma.split('#')[0].split('-')[0]
        wn31lemma[wnoffset[1:]] = lemma

def verbalize_clusters(frame_instances, clusters, clusters_verbalize_path):
    text_dict = {}

    for id_cluster, cluster in clusters.items():
        frame = frame_instances[cluster['center']]
        text_dict[id_cluster] = {}
        text_dict[id_cluster]['center'] = verbalize_frame(frame.frame_elements, frame.frame_type)
        elements = []
        for id_frame in cluster['elements']:
            frame = frame_instances[id_frame]
            elements.append(verbalize_frame(frame.frame_elements, frame.frame_type))

        text_dict[id_cluster]['elements'] = elements

    save_json(text_dict, clusters_verbalize_path)

def verbalize_frame(frame_elements, frame_type):
    text_list = []
    
    for frame_element in frame_elements:
        wn31id = frame_element.entity[1:-1].split('/')[-1]
        if wn31id in wn31lemma:
            text_list.append("'%s' is the '%s'" % (wn31lemma[wn31id].replace('+', ' '), frame_element.role))

    return "In frame %s " % frame_type.upper() + ' and '.join(text_list)

def load_json(json_path):
    with open(json_path) as fin:
        data = json.load(fin)

    return data

def save_json(data, json_path, sort_keys=True):
    with open(json_path, "w") as fout:
        json.dump(data, fout, indent=4, sort_keys=sort_keys)


if __name__ == '__main__':
    start_time = datetime.now()
    triples_path = join(dirname(__file__), 'input/')
    clusters_path = join(dirname(__file__), 'output/clusters.json')
    clusters_verbalize_path = join(dirname(__file__), 'output/clusters_verbalize.json')

    logging.info('Reading dataset')
    frame_instances = read_dataset(triples_path, delete_repetition=False)
    logging.info('Reading clusters')
    clusters = load_json(clusters_path)
    logging.info('Verbalizing clusters')
    verbalize_clusters(frame_instances, clusters, clusters_verbalize_path)

    end_time = datetime.now()
    logging.info('Duration {}'.format(end_time - start_time))
