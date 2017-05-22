__Author__ = "Avijit Shah"

import mechanize
import lxml.html
import logging
from modules_read_write import *
from goose import Goose
import os
import sys, getopt
PATH_current = os.path.abspath('form_fill_and_Extract.py')
PATH_Package = "/".join(PATH_current.split('/')[:-1])

LOG_FILENAME = "logger.txt"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG)
logging.debug('This message should go to the log file')
RESOURCE_CODE = "wp"
inputfile = "input.txt"
INPUT_DBPEDIA_UID = True    #if the entities given as input are all DBPEIDA UID, then it's uid stored in final dict else not
#note: set it to false if crawling for entities that are not extracted from DBPEDIA UID

#import nltk          #download stop words corpora for the first time
#nltk.download()
def main(argv):
    global inputfile  #will contain all the keyphrases to search(either extracted from DBpedia uid or new one.. both fine)
    global RESOURCE_CODE #tells the web resource from where to crawl
    try:
        opts, args = getopt.getopt(argv, "hi:r:",
                                   ["ifile", "resource="])
    except getopt.GetoptError:
        print 'form_fill_and_Extract.py -i <inputfile> -r <web resource code - wikipedia:wp, wikihow:wh, reference:rf, thoughtco:tc, ehow:eh, howstuffworks:hw, infoplease:ip  > '
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'form_fill_and_Extract.py -i <inputfile> -r <type web-resource code - wikipedia:wp, wikihow:wh, reference:rf, thoughtco:tc, ehow:eh, howstuffworks:hw, infoplease:ip  > '
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
            #print inputfile
        elif opt in ("-r", "--resource"):
            RESOURCE_CODE = str(arg)

    if len(args) >= 1:
        inputfile = args[0]


def set_resource_url():
    if(RESOURCE_CODE == "wp"):
        resource = "https://en.wikipedia.org/wiki/Special:Search"
        directory = "Wikipedia"
    elif (RESOURCE_CODE == "wh"):
        resource = "http://www.wikihow.com/Main-Page"
        directory = "Wikihow"
    elif (RESOURCE_CODE == "rf"):    #some issue
        resource = "https://www.reference.com/"
        directory = "Reference"
    elif (RESOURCE_CODE == "tc"):
        resource = "https://www.thoughtco.com/"
        directory = "Thoughtco"
    elif (RESOURCE_CODE == "eh"):
        resource = "http://www.ehow.com/"
        directory = "ehow"
    elif (RESOURCE_CODE == "hw"):
        resource = "http://www.howstuffworks.com/"
        directory = "howstuffworks"
    elif (RESOURCE_CODE == "ip"):
        resource = "https://www.infoplease.com/"
        directory = "infoplease"
    return resource, directory

def check_condition(page):
    title_by_goose = page.title
    if(len(title_by_goose)> 0):
        #if(title_by_goose.endswith("Warnings") or title_by_goose.endswith("Side Effects") or title_by_goose.endswith("Safety Info")):
        return True   #since in this case only direct links to wikipedia pages are given
    else:
        return False


def extract_articles(list_links, data_store, resource_dir, dbpedia_entity):
    #keyphrase = keyphrase.replace(" ", "_")
    count = 0
    #data_store = {}
    unopened_url = []
    for link in list_links:
        try:
            count+=1
            g = Goose()
            page = g.extract(link)
            domain = page.domain
            filename = str(count) + "_" + link.split("/")[-1] + ".txt"
            if (check_condition(page) == True):
                #print "entered"
                title_by_goose = page.title
                extracted_info = {}
                #title = ' '.join(title_by_goose.split(' ')[1:]) #set according to condition to grab correct title for ESL site
                title = title_by_goose
                article = page.cleaned_text
                meta_description = page.meta_description
                authors = page.authors                    #it's a list, as author could be multiple
                published_dates = page.publish_date
                #since story type is unicode, not string
                lines = 0
                words = 0
                para = 1
                resource_directories = [x[0].split("/")[-1] for x in os.walk(PATH_Package + "/data/")]
                if(resource_dir not in resource_directories):
                    subprocess.call(["mkdir " + PATH_Package + "/data/" + resource_dir], shell=True)
                directories = [x[0].split("/")[-1] for x in os.walk(PATH_Package + "/data/"+resource_dir)]
                #print directories
                flag = 0
                if(count==1 and (dbpedia_entity not in directories)):
                    #print "avijit shah"
                    directory = dbpedia_entity
                    if ("(" in dbpedia_entity):  # bcoz parenthesis in variable name in command cause problem in execution
                        directory = "\\(".join(directory.split("("))
                        flag = 1
                    if (")" in dbpedia_entity):
                        directory = "\\)".join(directory.split(")"))
                        flag=1
                    if ("'" in dbpedia_entity):
                        directory = "\\'".join(directory.split("'"))
                        flag=1
                    if(flag==1):
                        subprocess.call(["mkdir " + PATH_Package + "/data/" + resource_dir + "/" + directory], shell = True)
                    else:
                        subprocess.call(["mkdir " + PATH_Package + "/data/" + resource_dir + "/" + dbpedia_entity], shell=True)
                write_article_txt(article, filename, dbpedia_entity, resource_dir)
                filter_text(filename, dbpedia_entity, resource_dir)
                article = read_file(filename, dbpedia_entity, resource_dir)
                if(len(article)!=0):
                    for letter in article:
                        if(letter=='.'):
                            lines+=1
                        elif(letter==' '):
                            words+=1
                        elif(letter=='\n'):
                            para+=1
                extracted_info['title']= title
                extracted_info['article']= article
                extracted_info['para'] = para
                extracted_info['domain']= domain
                extracted_info['lines']= lines
                extracted_info['words']= words
                extracted_info['meta_description']= meta_description
                extracted_info['authors']= authors
                extracted_info['published_dates']= published_dates
                extracted_info['story_name'] = filename
                extracted_info['entity'] = dbpedia_entity
                extracted_info['resource']= resource_dir
                if(INPUT_DBPEDIA_UID == True):
                    extracted_info['dbpedia_uid'] = "http://dbpedia.org/resource/" + dbpedia_entity
                else:
                    extracted_info['dbpedia_uid'] = None
                if (len(article) != 0):                       #it's 2nd check as condition above may lead to some page that has title but not story
                    data_store[link] = extracted_info
                    print count, "link", link, "\nTitle", data_store[link]['title']#, "\nStory", data_store[link]['article'], "\nParagraph", data_store[link]['para'], \
                    #"\ndomain:",data_store[link]['domain'], "\nlines:",data_store[link]['lines'], "\nwords:",data_store[link]['words'],"\nmeta_description:",\
                    #data_store[link]['meta_description'],"\nauthor",data_store[link]['authors'],"\npublished_date:",data_store[link]['published_dates'], "\n"

        except:
            unopened_url.append(link)
            write_to_file(0, str(link), "", "unscrapped_wikipedia.txt")
            print "error"
    return data_store

def fill_form(url, keyphrase, data_store, resource_dir, DBpedia_entity):
    if(len(keyphrase)==0):
        return False
    set_links = set()
    br = mechanize.Browser()
    br.set_handle_robots(False) # ignore robots
    br.open(url)
    br.form = list(br.forms())[0]
    splitted_keyphrase = keyphrase.split(" ")
    #print splitted_keyphrase
    try:
        for control in br.form.controls:
            content = None
            if(not str(control).endswith("(readonly)>")):
                control.value = keyphrase
                response = br.submit()
                content = response.read()
                #print content
                with open("result.html", "w") as f:
                    f.write(content)
                break

        #to extract the links
        if(url == "http://www.wikihow.com/Main-Page"):
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):  # select the url in href for all a tags(links)
                val = 1
                link = link.encode('utf-8').split("?")[0]
                #print str(link).lower()
                for k in splitted_keyphrase:
                    if(k in str(link).lower()): #need to put better condition, now temporarily
                        val = val*1
                    else:
                        val = 0
                        break
                if(val == 1):
                    link = "http:"+link
                    print link
                    set_links.add(link)

        elif(url == "https://en.wikipedia.org/wiki/Special:Search"):
            #put if condition to first check the map,then this
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):  # select the url in href for all a tags(links)
                val = 1
                link = link.encode('utf-8').split("?")[0]
                #print str(link).lower()
                for k in splitted_keyphrase:
                    if (k in str(link).lower()):  # need to put better condition, now temporarily
                        val = val*1
                    else:
                        val = 0
                        break
                if(val==1):
                    link = "https://en.wikipedia.org" + link
                    print link
                    set_links.add(link)

        elif (url == "https://www.reference.com/"):
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):  # select the url in href for all a tags(links)
                val = 1
                link = link.encode('utf-8')
                #print str(link).lower()
                for k in splitted_keyphrase:
                    if (k in str(link).lower()):  # need to put better condition, now temporarily
                        val = val*1
                    else:
                        val = 0
                        break
                if(val==1):
                    if(str(link).startswith("http") == False):
                        link = "https://" + link.strip("/")
                    print link
                    set_links.add(link)

        elif (url == "https://www.thoughtco.com/"):
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):  # select the url in href for all a tags(links)
                val = 1
                link = link.encode('utf-8')
                # print str(link).lower()
                for k in splitted_keyphrase:
                    if (k in str(link).lower()):  # need to put better condition, now temporarily
                        val = val*1
                    else:
                        val = 0
                        break
                if(val==1):
                    link = link.strip("/")
                    print link
                    set_links.add(link)

        elif (url == "http://www.ehow.com/"):
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):  # select the url in href for all a tags(links)
                val = 1
                link = link.encode('utf-8')
                # print str(link).lower()
                for k in splitted_keyphrase:
                    if (k in str(link).lower()):  # need to put better condition, now temporarily
                        val = val*1
                    else:
                        val = 0
                        break
                if(val==1):
                    link = link.strip("/")
                    print link
                    set_links.add(link)

        elif (url == "http://www.howstuffworks.com/"):
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):  # select the url in href for all a tags(links)
                val = 1
                link = link.encode('utf-8')
                # print str(link).lower()
                for k in splitted_keyphrase:
                    if (k in str(link).lower()):  # need to put better condition, now temporarily
                        val = val*1
                    else:
                        val = 0
                        break
                if(val==1):
                    link = link.strip("/")
                    print link
                    set_links.add(link)


        elif (url == "https://www.infoplease.com/"):
            dom = lxml.html.fromstring(content)
            for link in dom.xpath('//a/@href'):  # select the url in href for all a tags(links)
                val = 1
                link = link.encode('utf-8')
                # print str(link).lower()
                for k in splitted_keyphrase:
                    if (k in str(link).lower()):  # need to put better condition, now temporarily
                        val = val*1
                    else:
                        val = 0
                        break
                if(val==1):
                    link = link.strip("/")
                    print link
                    set_links.add(link)


    except:
        logging.exception('Unable to search for:' + keyphrase)
        #raise

    list_links = list(set_links)
    if(len(list_links)==0):
        return False
    data_store = extract_articles(list_links, data_store, resource_dir, DBpedia_entity)
    return True


def refine(keyphrase):
    from nltk.corpus import stopwords
    import nltk
    stop = set(stopwords.words('english'))
    substituted_kp = str(keyphrase).replace("_", " ")
    parse_tree = nltk.ne_chunk(nltk.tag.pos_tag(substituted_kp.split()), binary=True)
    named_entities = []
    for t in parse_tree.subtrees():
        if t.label() == 'NE':
            named_entities.append(t)
            # named_entities.append(list(t))  # if you want to save a list of tagged words instead of a tree
    NE = []
    for tree in named_entities:
        temp = [tuple[0] for tuple in tree]
        NE.append(" ".join(temp))
    #print NE
    string_list = [i for i in substituted_kp.lower().strip("\n").split(" ") if i not in stop]
    #print string_list
    #print keyphrase,
    #print substituted_kp,
    #print NE,
    #print string_list,
    return substituted_kp, NE, string_list


if __name__ == "__main__":
    main(sys.argv[1:])
    search_resource, directory = set_resource_url()
    keyphrases = read_file_lines(inputfile)
    data_store = {}
    bool = False
    for keyphrase in keyphrases:
        FLAG = 0
        refined_keyphrase, Named_Entity, keyphrase_list = refine(keyphrase)
        if(fill_form(search_resource, refined_keyphrase.strip("\n").lower(), data_store, directory, keyphrase.strip("\n")) == True):
            print "Searched Actual entity:", refined_keyphrase.strip("\n").lower()
            print "\n"
            continue
        elif(fill_form(search_resource, " ".join(Named_Entity).lower(), data_store, directory, keyphrase.strip("\n")) == True):
            print "No results for actual entity:", refined_keyphrase.strip("\n").lower()
            print "Searched for Named Entity:", " ".join(Named_Entity).lower()
            print "\n"
            continue
        else:
            print "No result found for actual keyphrase-",refined_keyphrase.strip("\n").lower(), "or Named Entity-"," ".join(Named_Entity).lower()," in keyphrase..."
            print "No article found"
            print "\n"

    #for key in data_store:
        #print key, data_store[key]
    write_to_file_json(data_store,"dict_"+directory+".json")
