from os import path
import json
import subprocess
import re

PATH_current = path.abspath('modules_read_write.py')
PATH_Package = "/".join(PATH_current.split('/')[:-1])

def write_to_file(count, dbpedia_uid, link, fname):
    with open(PATH_Package + "/metadata/" + fname, 'a') as fp:
        fp.write(str(count) + "\t" + dbpedia_uid + "\t" + link + "\n")

def read_file(filename, directory, resource_dir):
    fp = open(PATH_Package + "/data/" + resource_dir + "/" +directory+"/"+ filename, "r")
    article = fp.read()
    return article

def read_file_lines(filename):
    fp = open(filename)
    text = fp.readlines()
    return text

def load_index():
    text_file = open("seed.txt", "r")
    seed_links = text_file.readlines()
    return seed_links

def write_stories_txt(data_store):
    print "writing stories to files.."
    count = 1
    for key in data_store:
        with open(PATH_Package + "/data/" + str(count) + "_" + data_store[key]['story'].split(" ")[0] + ".txt", 'wt') as fp:
            fp.write(data_store[key]['story'].encode("utf-8"))
            fp.close()
            count+=1
    print count, "files written properly.."

def write_article_txt(article, filename, directory, resource_dir):
    with open(PATH_Package + "/data/"+ resource_dir + "/"+ directory+"/"+filename,'wt') as fp:
        fp.write(article.encode("utf-8"))
        fp.close()


def write_to_file_json(data, name):
    print "dumping info to JSON files.."
    with open(PATH_Package+"/metadata/" + name, 'wt') as fp:
        json.dump(data, fp, indent=2, encoding = "utf-8")
    print "dumped successfully.."


def filter_text(filename, directory, resource_dir):
    if ("(" in directory):  # bcoz parenthesis in variable name in command cause problem in execution
        directory = "\\(".join(directory.split("("))
    if (")" in directory):
        directory = "\\)".join(directory.split(")"))
    if ("'" in directory):
        directory = "\\'".join(directory.split("'"))
    if("(" in filename):  #bcoz parenthesis in variable name in command cause problem in execution
        filename = "\\(".join(filename.split("("))
    if(")" in filename):
        filename = "\\)".join(filename.split(")"))
    if ("'" in filename):
        filename = "\\'".join(filename.split("'"))
    subprocess.call(["sed -i -e '/^\s*$/d' " + PATH_Package + '/data/' + resource_dir + "/" + directory + "/" + filename],shell=True)
    subprocess.call(["sed -i -e 's/^[^A-Z]*//g' " + PATH_Package + '/data/' + resource_dir + "/" + directory + "/" + filename],shell=True)
    subprocess.call(["sed -i -e 's/\[[0-9]*\]//g' "  + PATH_Package + '/data/' + resource_dir + "/" + directory + "/" + filename],shell=True)

    print "success"

def load_JSON(filename):
    with open(PATH_Package + "/metadata/" + filename) as fp:
        return json.load(fp)


def write(list, filename):
    with open(PATH_Package + "/data/" +filename,'wt') as fp:
        for link in list:
            fp.write(link)

        fp.close()
