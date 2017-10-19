# -*- coding: utf-8 -*

import json
import logging
import networkx as nx
from datetime import datetime
from os.path import join, dirname
from reduce_dataset import read_dataset
from pyspark import SparkContext, SparkConf, StorageLevel
from frameinstancesimilarity import frame_relatedness, synset_similarity, frame_instance_similarity

THRESHOLD = 0.2
READ_PRECALCULATION = True

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')#, filename='clustering.log')

spark_conf = [('spark.driver.memory', '10g'), ('spark.driver.maxResultSize', '0'),
            ('spark.executor.memory', '10g'), ('spark.hadoop.validateOutputSpecs', 'false'),
            ('spark.driver.bindAddress', '127.0.0.1'), ('spark.local.dir', join(dirname(__file__), 'spark/'))]

conf = SparkConf().setAppName('Clustering').setMaster('local[*]').setAll(spark_conf)
sc = SparkContext(conf=conf)

cache_frames = {}
cache_synsets = {}


def calculate_mst(frame_instances, mst_path, k=4):
    complete_subsets = create_complete_subsets(frame_instances.keys())
    bipartite_subsets = create_bipartite_subsets(complete_subsets)
    num_subgraphs = len(complete_subsets) + len(bipartite_subsets)
    start = len(complete_subsets)

    rdd_complete_subgraphs = sc.parallelize([(i, x) for i,x in enumerate(complete_subsets)])
    rdd_complete_mst = rdd_complete_subgraphs.mapValues(lambda x: map_mst_complete(x, frame_instances))
    rdd_complete_mst.persist(StorageLevel.MEMORY_AND_DISK)
    rdd_bipartite_subgraphs = sc.parallelize([(i+start, x) for i,x in enumerate(bipartite_subsets)])
    rdd_bipartite_mst = rdd_bipartite_subgraphs.mapValues(lambda x: map_mst_bipartite(x, frame_instances))
    rdd_bipartite_mst.persist(StorageLevel.MEMORY_AND_DISK)
    rdd_mst = rdd_complete_mst.union(rdd_bipartite_mst)


    while num_subgraphs > 1:
        num_subgraphs = (num_subgraphs + k - 1) / k
        rdd_mst = rdd_mst.map(lambda (x,y): (x / k, y))
        rdd_mst = rdd_mst.reduceByKey(lambda x,y: reduce_mst(x,y))

    rdd_mst.persist(StorageLevel.MEMORY_AND_DISK)
    rdd_mst.saveAsPickleFile(mst_path)
    rdd_mst.unpersist()

def calculate_clusters(frame_instances, repeated_instances, mst_path, clusters_path, clusters_json_path):
    rdd_mst = sc.pickleFile(mst_path)
    rdd_clusters = rdd_mst.flatMap(lambda (x, y): extract_clusters(y))
    rdd_clusters = rdd_clusters.flatMapValues(lambda x: [(i, x) for i in x])
    rdd_clusters = rdd_clusters.mapValues(lambda x: map_medoid_distances(x, frame_instances, repeated_instances))
    rdd_clusters = rdd_clusters.reduceByKey(lambda x,y: reduce_medoid_distances(x,y))
    rdd_clusters = rdd_clusters.mapValues(lambda x: {'center':x['center'], 'elements':x['elements']})
    rdd_clusters.saveAsPickleFile(clusters_path)
    clusters_dict = rdd_clusters.collectAsMap()

    save_json(clusters_dict, clusters_json_path)

def create_complete_subsets(instances, instances_x_subset=500):
    min_index = 0
    size = len(instances)
    subsets = []

    while min_index < size:
        max_index = min_index + instances_x_subset
        subsets.append(instances[min_index: max_index])
        min_index = max_index

    return subsets

def create_bipartite_subsets(subsets):
    size = len(subsets)
    new_subsets = []

    for i in xrange(size):
        for j in xrange(i+1, size):
            new_subsets.append({'left':subsets[i], 'right':subsets[j]})

    return new_subsets

def map_mst_complete(subset, frame_instances):
    logging.debug('Calculating MST in completed graph')
    graph = nx.Graph()
    size = len(subset)

    for i in xrange(size):
        id_frame1 = subset[i]
        for j in xrange(i+1, size):
            id_frame2 = subset[j]
            distance = calculate_distance_measure(frame_instances[id_frame1], frame_instances[id_frame2])
            graph.add_edge(id_frame1, id_frame2, weight=distance)

    return list(nx.prim_mst_edges(graph, data=True))

def map_mst_bipartite(subset, frame_instances):
    logging.debug('Calculating MST in bipartite graph')
    graph = nx.Graph()

    for id_frame1 in subset['left']:
        for id_frame2 in subset['right']:
            distance = calculate_distance_measure(frame_instances[id_frame1], frame_instances[id_frame2])
            graph.add_edge(id_frame1, id_frame2, weight=distance)

    return list(nx.prim_mst_edges(graph, data=True))

def reduce_mst(mst1, mst2):
    logging.debug('Reducing MST')
    graph = nx.Graph()

    for node1, node2, distance in mst1:
        graph.add_edge(node1, node2, weight=distance['weight'])

    for node1, node2, distance in mst2:
        graph.add_edge(node1, node2, weight=distance['weight'])

    return list(nx.minimum_spanning_edges(graph, data=True))

def extract_clusters(tuple_list, min_elements=3):
    graph = nx.Graph()
    id_cluster = 0
    clusters = []

    for node1, node2, distance in tuple_list:
        if  distance['weight'] < THRESHOLD:
            graph.add_edge(node1, node2, weight=distance['weight'])

    for subgraph in nx.connected_components(graph):
        if len(subgraph) >= min_elements:
            clusters.append((id_cluster, list(subgraph)))
            id_cluster += 1

    return clusters

def map_medoid_distances(pair, frame_instances, repeated_instances):
    logging.debug('Calculating medoid distances')
    current_node = pair[0]
    nodes = pair[1]
    other_instances = []
    global_distance = 0

    for node in nodes:
        if node != current_node:
            distance = calculate_distance_measure(frame_instances[current_node], frame_instances[node])
            global_distance += (distance * (1 + len(repeated_instances[node])))

    return {'center':current_node, 'elements':[current_node] + repeated_instances[current_node], 'distance':global_distance}

def reduce_medoid_distances(medoid_data1, medoid_data2):
    logging.debug('Reducing medoid distances')
    min_distance = None
    medoid = None

    if medoid_data1['distance'] < medoid_data2['distance']:
        min_distance = medoid_data1['distance']
        medoid = medoid_data1['center']
    else:
        min_distance = medoid_data2['distance']
        medoid = medoid_data2['center']

    return {'center':medoid, 'elements':medoid_data1['elements'] + medoid_data2['elements'], 'distance':min_distance}

def extract_corpus_statistics(frame_instances):
    frames = {}
    synsets = {}

    for frame_instance in frame_instances.values():
        frames[frame_instance.frame_type] = frames.get(frame_instance.frame_type, 0) + 1
        for frame_element in frame_instance.frame_elements:
            synset_id = frame_element.entity
            synsets[synset_id] = synsets.get(synset_id, 0) + 1

    return frames, synsets

def precalculate_similarities(frames, synsets, cache_frames_path, cache_synsets_path, top_synsets=3000, ftsim='occ', fesim='wup'):
    frame_list = frames.keys()
    size = len(frame_list)
    tuple_list = []
    for i in xrange(size):
        for j in xrange(i+1, size):
            tuple_list.append((frame_list[i], frame_list[j]))

    cache_frames = create_cache(tuple_list, frame_relatedness, ftsim) 

    synset_list = sorted(synsets.items(), key=lambda x:x[1], reverse=True)[:top_synsets]
    size = len(synset_list)
    tuple_list = []
    for i in xrange(size):
        synsetid1 = synset_list[i][0]
        for j in xrange(i+1, size):
            synsetid2 = synset_list[j][0]
            tuple_list.append((synsetid1, synsetid2))

    cache_synsets = create_cache(tuple_list, synset_similarity, fesim)

    save_json(cache_frames, cache_frames_path, False)
    save_json(cache_synsets, cache_synsets_path, False)

    return cache_frames, cache_synsets

def create_cache(tuple_list, function_measure, measure):
    rdd_tuple = sc.parallelize(tuple_list)
    rdd_tuple = rdd_tuple.map(lambda (x,y): (x, {y: function_measure(x, y, measure)}))
    rdd_tuple = rdd_tuple.reduceByKey(lambda x,y: merge_dicts(x, y))
    tuple_dict = rdd_tuple.collectAsMap()
    rdd_tuple.unpersist()

    return tuple_dict

def calculate_distance_measure(instance_frame1, instance_frame2):
    return 1 - frame_instance_similarity(instance_frame1, instance_frame2, cache_frames=cache_frames, cache_synsets=cache_synsets)

def merge_dicts(*dict_args):
    result = {}

    for dictionary in dict_args:
        result.update(dictionary)

    return result

def load_json(json_path):
    with open(json_path) as fin:
        data = json.load(fin)

    return data

def save_json(data, json_path, sort_keys=True):
    with open(json_path, "w") as fout:
        json.dump(data, fout, indent=4, sort_keys=sort_keys)

if __name__ == '__main__':
    start_time = datetime.now()
    global cache_frames
    global cache_synsets

    triples_path = join(dirname(__file__), 'input/')
    repeated_instances_path = join(dirname(__file__), 'output/ehow_repeated_instances.json')
    cache_frames_path = join(dirname(__file__), 'output/cache_frames.json')
    cache_synsets_path = join(dirname(__file__), 'output/cache_synsets.json')
    mst_path = join(dirname(__file__), 'output/ehow_mst')
    clusters_path = join(dirname(__file__), 'output/ehow_clusters')
    clusters_json_path = join(dirname(__file__), 'output/ehow_clusters.json')

    logging.info('Reading dataset')
    frame_instances = read_dataset(triples_path, repeated_instances_path)
    if READ_PRECALCULATION:
        cache_frames = load_json(cache_frames_path)
        cache_synsets = load_json(cache_synsets_path)
    else:
        logging.info('Extracting corpus statistics')
        frames, synsets = extract_corpus_statistics(frame_instances)
        logging.info('Precalculating similarities')
        cache_frames, cache_synsets = precalculate_similarities(frames, synsets, cache_frames_path, cache_synsets_path)

    logging.info('Calculating MST')
    calculate_mst(frame_instances, mst_path)
    logging.info('Calculating clusters')
    repeated_instances = {v[0]:v[1:] for v in load_json(repeated_instances_path).values()}
    calculate_clusters(frame_instances, repeated_instances, mst_path, clusters_path, clusters_json_path)

    end_time = datetime.now()
    logging.info('Duration {}'.format(end_time - start_time))