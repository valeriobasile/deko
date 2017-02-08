#!/usr/bin/env python

from nltk.corpus import wordnet as wn
#import nltk
#from path import path
import json
import re
import sys, getopt
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, ward, fcluster
from scipy.spatial.distance import squareform, pdist
import time
import scipy


#PATH_current = path('src.py').abspath()
#PATH_Package = "/".join(PATH_current.split('/')[:-1])

FLAG_FRAME = "WUP"  # select algorithm for similarity between two frame types
FLAG_ELEMENTS = "WUP"  # select algorithm for similarity between two elements
ALPHA = 0.5  # constant for main formula
ROLE = "false"
clustering_method = "weighted"
DISTANCE = 1
inputfile = "./samples/test_sample1.nt"
#nltk.download()
CACHE = True

unmapped_keys = set()  # those occur in any input instance

if CACHE:
    sys.stderr.write('reading similarity cache...\n')
    synset_similarity_matrix = dict()
    with open('synset_similarity_matrix.txt') as f:
        for line in f:
            sim, s1, s2 = line.rstrip().split(' ')
            synset_similarity_matrix[(s1,s2)]=sim
            synset_similarity_matrix[(s2,s1)]=sim

def main(argv):
    global inputfile
    global FLAG_FRAME
    global FLAG_ELEMENTS
    global ROLE
    global ALPHA
    global clustering_method
    global DISTANCE
    try:
        opts, args = getopt.getopt(argv, "hi:a:t:e:r:m:d:",
                                   ["ifile", "alpha=", "F_Sim_Algo=", "E_Sim_Algo=", "role=", "method=", "distance="])
    except getopt.GetoptError:
        print 'clustering.py -i <inputfile> -a <alpha value> -t <Frame_similarity_Algo> -e <element_similarity_Algo> -r <true,false> -m <single, complete, average, weighted, centroid, median, ward> -d <distance(greater than 0) range to be considered in same cluster>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'clustering.py -i <inputfile>  -a <alpha value> -t <Frame_similarity_Algo> -e <element_similarity_Algo> -r <true,false> -m <single, complete, average, weighted, centroid, median, ward> -d <distance(greater than 0) range to be considered in same cluster>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            #print inputfile
        elif opt in ("-a", "--alpha"):
            ALPHA = float(arg)
        elif opt in ("-t", "--F_Sim_Algo"):
            FLAG_FRAME = arg
        elif opt in ("-e", "--E_Sim_Algo"):
            FLAG_ELEMENTS = arg
        elif opt in ("-r", "--role"):
            ROLE = arg
        elif opt in ("-m", "--method_clustering"):
            clustering_method = arg
        elif opt in ("-d", "--clustering_distance"):
            DISTANCE = arg
    if len(args) >= 1:
        inputfile = args[0]



def dump_JSON(dict, filename):
    with open(filename, 'w') as fp:
        json.dump(dict, fp)

def load_JSON(filename):
    with open(filename) as fp:
        return json.load(fp)


def read_file(filename):
    fp = open(filename, "r")
    return fp.readlines()


def extract_F_instance_elements(frame_instances):
    frame_dict = {}
    for frame_instance in frame_instances:
        try:
            F_instance = re.findall("(?<=fi-)([a-zA-Z_0-9-]*)", str(frame_instance))
            F_name_offset = re.findall("(?<=frame-)([a-zA-Z_0-9-]*)", str(frame_instance))
            F_offset = "-".join(F_name_offset[0].split("-")[1:])
            F_elements = re.findall("(?<=wn31/)([a-zA-Z_0-9-]*)", str(frame_instance))
            F_roles = re.findall(r"(?<=fe-)([a-zA-Z_ -]*)", str(frame_instance))
            F_elements_roles = [(F_elements[i], F_roles[i]) for i in range(len(F_elements))]
            F_instance_offset = F_instance[0] + "_" + F_offset
            frame_dict[F_instance_offset] = (F_elements_roles)
        except:
            pass
            #print
            #print F_instance, "reg ex error caught"
    # print "Frame_instance-elements Dictionary:\n",frame_dict,"\n"
    #print "Frame instance and elements' extraction successful..... dictionary ready"
    return frame_dict


def offset2ss(offset_31, wn_31_30):
    try:
        # convert wordnet 3.1 id to 3.0 because NLTK limited to 3.0 for now
        offset_30 = wn31_30[offset_31]
        synset = wn._synset_from_pos_and_offset(str(offset_30[-1:]), int(offset_30[:8]))
    # print "offset_31:", offset_31, "\toffset_30:", offset_30, "\tsynset:", synset
    # print type(wn._synset_from_pos_and_offset(str(offset_30[-1:]), int(offset_30[:8])))
    except:
        # print "key", offset_31, "is not mapped.."           #handling the mapping issue between wn3.1 and wn3.0
        # print "score given is 0"
        unmapped_keys.add(offset_31)
        synset = None
    return synset


def WUP_similarity(ss1, ss2, cache=False):
    if (ss1 is None or ss2 is None):  # due to mapping issue b/w wn3.1 and wn3.2
        return 0.0
    return wn.wup_similarity(ss1, ss2)


def find_similarity_frames(frameType1_offset, elements1_offsets_role, frameType2_offset, elements2_offsets_role,
                           wn31_30):
#    print "Frame type synsets:"
    synset_F1 = offset2ss(frameType1_offset, wn31_30)
    synset_F2 = offset2ss(frameType2_offset, wn31_30)
    if FLAG_FRAME == "WUP":
        similarity_F_types = WUP_similarity(synset_F1, synset_F2, CACHE)
#        print "simialrity F type", synset_F1, synset_F2, similarity_F_types
        # Add other conditions and respective similarity calculating functions
#    print "Elemnents_synsets:"
    elements1_synsets_role = [(offset2ss(element[0], wn31_30), element[1]) for element in elements1_offsets_role]
    elements2_synsets_role = [(offset2ss(element[0], wn31_30), element[1]) for element in elements2_offsets_role]
#    print "elements1_synsets:\t", elements1_synsets_role
#    print "elements2_synsets:\t",elements2_synsets_role
    # bipartitie, thus do both ways
#    print "Calculating Left2Right_elements_similarities..."
    sum_similarity = 0
    for el_r_F1 in elements1_synsets_role:
        max_similarity = 0
        el_F1 = el_r_F1[0]
        r_F1 = el_r_F1[1]
        for el_r_F2 in elements2_synsets_role:
            el_F2 = el_r_F2[0]
            r_F2 = el_r_F2[1]

            #print el_F1, el_F1.min_depth(), el_F1.max_depth()
            #print el_F2, el_F2.min_depth(), el_F2.max_depth()

            if (ROLE == "false"):
                if (FLAG_ELEMENTS == "WUP"):
                    similarity_element = WUP_similarity(el_F1, el_F2, CACHE)
                    # Add other conditions and respective similarity calculating functions
            elif (ROLE == "true"):
                if (r_F1 == r_F2):
                    if (FLAG_ELEMENTS == "WUP"):
                        similarity_element = WUP_similarity(el_F1, el_F2, CACHE)
                        # Add other conditions and respective similarity calculating functions
                else:
                    similarity_element = 0
            #print similarity_element
#            print "similarity between",el_F1,el_F2,":\t",similarity_element
            if (similarity_element > max_similarity):
                max_similarity = similarity_element
#        print "max_similarity for",el_F1,":\t", max_similarity
        sum_similarity = max_similarity + sum_similarity
    avg_similarity_1 = sum_similarity / len(elements1_synsets_role)
#    print "avg_similarity_L2R:\t", avg_similarity_1

#    print "Calculating Right2left_elements_similarities..."
    sum_similarity = 0
    for el_r_F2 in elements2_synsets_role:
        max_similarity = 0
        el_F2 = el_r_F2[0]
        r_F2 = el_r_F2[1]
        for el_r_F1 in elements1_synsets_role:
            el_F1 = el_r_F1[0]
            r_F1 = el_r_F1[1]
            if (ROLE == "false"):
                if (FLAG_ELEMENTS == "WUP"):
                    similarity_element = WUP_similarity(el_F1, el_F2, CACHE)
                    #Add other conditions and respective similarity calculating functions
            elif (ROLE == "true"):
                if (r_F1 == r_F2):
                    if (FLAG_ELEMENTS == "WUP"):
                        similarity_element = WUP_similarity(el_F1, el_F2, CACHE)
                        # Add other conditions and respective similarity calculating functions
                else:
                    similarity_element = 0
#            print "similarity between", el_F2, el_F1,":\t", similarity_element
            if (similarity_element > max_similarity):
                max_similarity = similarity_element
#        print "max_similarity for",el_F2,":\t", max_similarity
        sum_similarity = max_similarity + sum_similarity
    avg_similarity_2 = sum_similarity / len(elements2_synsets_role)
#    print "avg_similarity_R2L:\t", avg_similarity_2

    avg_similarity = (avg_similarity_1 + avg_similarity_2) / 2
#    print "Avg_both_sides_similarities:\t", avg_similarity
    if (similarity_F_types is None):
        similarity_F_types = 0.0
    if (avg_similarity is None):
        avg_similarity = 0.0
    similarity_Frames = ALPHA * (similarity_F_types) + (1 - ALPHA) * (avg_similarity)
#    print "FType_similarity\t", synset_F1, synset_F2, ":\t", similarity_F_types
#    print "Similarity Frame instance:", similarity_Frames,"\n"
    return similarity_Frames


def merge(Instance_1, Instance_2):
    frame_instances = []
    frame_instances.append(Instance_1)
    frame_instances.append(Instance_2)
    return frame_instances


def triples_frame_instances(triples):
    frame_instances = []
    temp = []
    for i in range(len(triples)):
        F_instance1 = re.findall("(?<=fi-)([a-zA-Z_0-9-]*)", str(triples[i]))
        F_instance2 = re.findall("(?<=fi-)([a-zA-Z_0-9-]*)", str(triples[i - 1]))
        if (F_instance1[0] != F_instance2[0] or i == len(triples) - 1):
            if (i == len(triples) - 1):
                temp.append(triples[i])
            if (len(temp) != 0):
                frame_instances.append(temp)
            temp = []
            if (not F_instance1[0].startswith("Unmapped")):
                temp.append(triples[i])
            continue
        else:
            if (not F_instance1[0].startswith("Unmapped")):
                temp.append(triples[i])
    return frame_instances



def build_frame_distance_matrix(F_instance_element_dict):
    #print "building distance matrix...."
    Dist_Matrix = np.zeros(shape=(len(F_instance_element_dict), len(F_instance_element_dict))) #empty when printed shoes exponent val
    F_instance_element_tuple = F_instance_element_dict.items()
    frame_instance_index_dict = {}
    count = -1
    condensed_vector = []
    for i,key in enumerate(F_instance_element_tuple):
        progress = (float(i+1)*100.0)/ float(len(F_instance_element_tuple))
        sys.stderr.write('{0:.3f}%\t({1}/{2})\r'.format(progress, i+1, len(F_instance_element_tuple)))

        # frame1_name = str(key.split("_")[0])
        frameType1_offset = key[0].split("_")[-1]
        elements1_offsets_roles = key[1]
        frame_instance1 = "_".join(key[0].split("_")[:-1])
        frame_instance_index_dict[i] = frame_instance1
        count +=1
        count2 = 0
        #count2 = count
        for j, key2 in enumerate(F_instance_element_tuple):
            # frame2_name = str(key2.split("_")[0])
            frameType2_offset = key2[0].split("_")[-1]
            elements2_offsets_roles = key2[1]
            frame_instance2 = "_".join(key2[0].split("_")[:-1])
            if (count == count2):
                Dist_Matrix[count][count2] = 0
                #print frame_instance1, frame_instance2, Dist_Matrix[count][count2]
            elif(count2<count):
                Dist_Matrix[count][count2] = Dist_Matrix[count2][count]
            else:
                Dist_Matrix[count][count2] = 1 - find_similarity_frames(frameType1_offset, elements1_offsets_roles,
                                                                        frameType2_offset, elements2_offsets_roles,
                                                                        wn31_30)
                #print frame_instance1, frame_instance2, Dist_Matrix[count][count2]
                # condensed_vector.append(Dist_Matrix[count][count2])
            count2+=1

    #print "distance matrix succesfully built....."
    return Dist_Matrix, frame_instance_index_dict

def print_Dist_matrix(F_instance_distance_matrix, F_instance_index_dict):
    print F_instance_index_dict
    for i in F_instance_index_dict:
        print F_instance_index_dict[i]
    for row in F_instance_distance_matrix:
        for val in row :
                print val,"\t",
        print "\n"


def perform_clustering(Dist_matrix, F_instance_index_dict):
    #result_clusters = ward(Dist_matrix)
    #print "Beginnning clustering...."
    #print "method", clustering_method
    assignments = fcluster(linkage(Dist_matrix, method=clustering_method), DISTANCE, 'distance') #instead of weighted, can try others too
    #print "clustering performed successfully....."
    cluster = {}
    #print "printing clusters...."
    for i in range(len(assignments)):
        cluster[F_instance_index_dict[i]] = assignments[i]
        #print F_instance_index_dict[i],"\t", assignments[i]
    sorted_cluster = sorted(cluster.items(), key=lambda x: x[1])
    for tuple in sorted_cluster:
        print tuple[0], tuple[1]
    return sorted_cluster


def write_clusters(sorted_cluster):
    with open("clusters_role_false.txt", 'w') as fp:
        i = 0
        count = 0
        for pair in sorted_cluster:
            fp.write(str(pair[0])+"\t"+str(pair[1])+"\n")
    fp.close()

if __name__ == "__main__":
    start_time = time.time()
    main(sys.argv[1:])
    wn31_30 = load_JSON("map/JSON_wn31-30.json")  # load wn31-30 dictionary
    triples = read_file(inputfile)  # read file having triples where instances separated by blank line
    frame_instances = triples_frame_instances(triples)
    F_instance_element_dict = extract_F_instance_elements(frame_instances)  # generate dict carrying frame_instance as key and elements as values
    #print "total instances:",len(F_instance_element_dict)
    F_instance_distance_matrix, F_instance_index_dict = build_frame_distance_matrix(F_instance_element_dict)
    #print scipy.spatial.distance.is_valid_y(F_instance_distance_matrix)
    #print_Dist_matrix(F_instance_distance_matrix, F_instance_index_dict)
    sorted_cluster = perform_clustering(F_instance_distance_matrix, F_instance_index_dict)
    write_clusters(sorted_cluster)
    #print("--- %s seconds ---" % (time.time() - start_time))
