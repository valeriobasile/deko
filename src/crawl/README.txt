README
1. Instructions to run the code:
a) python form_fill_and_Extract.py -h     #this will show all the options that to be given as input
OUTPUT : form_fill_and_Extract.py -i <inputfile> -r <type web-resource code - wikipedia:wp, wikihow:wh, reference:rf, thoughtco:tc, ehow:eh, 		 howstuffworks:hw, infoplease:ip  > 
a.1) give options like wp, wh, rf etc. to choose which resource to search for
a.2) inputfile carries the list of DBpedia entities. Note: We can give any entity as input not just DBPedia entities
a.3) Code has a global variable "INPUT_DBPEDIA_UID". Set it to "True" if all the entities in the input file are DBpedia entities. This is because meta data dictionary then carry the DBpedia UID, otherwise it will be none.
a.4) "DBpedia_entites.txt" is the file carrying all the DBpedia entities extracted from the UID given. "input.txt" is the file made for test run where lesser numbers of keyphrases(entities) can be added to be given as input to the code to check how it works.
a.5) Don't use any space in the input entitites. Use underscore in place of space in the input file. Eg : Apple_tree is correct but not Apple tree

2. Requirements:
Run the code once. Method named refined(keyphrase) will raise error to download few nltk files. Uncomment "nltk.download()" and download all the files asking to download.

3. The arrangement of the data generated will be such that each resource will have a directory. Under each directory, there will be folders with entities names. Each Folder will be carrying the crawled text files about the entity from that resource.

4. JSON files corresponding to each resource will be generated in the metadata folder.

5. All the data extracted and stored are automatically filtered and analysed for the informations that is stored along with the content in JSON files.

6. The approach to search the entities is such that:(Algorithm)
6.1) Extract all the DBpedia entities from the DBPEdia UID list and store in a file. We have that file named as "DBPedia_entities.txt"
6.2) Use that entities(after normalization) to fill up the forms on various resources based on the user's input choice i.e value corresponding to "-r" option in the query to run the code.
6.2.1) Initially check putting the full phrase as it is(including stop words, non Named entities etc. )
6.2.2) If result is obtained, extract all the links obtained and then crawl, filter and save the content with meta info.
6.2.3) If not, find the "Named Entities" in the given entity to be searched. 
Eg: United_States_House_of_Representatives. Here search fails for United_States_House_of_Representatives thus, we consider the nearest possible search phrase i.e United_States_House.
6.2.4) From the extracted links after 6.2.2 or 6.2.3, we adopt a technique to choose only the useful links to extract data. The technique says, choose the links that will carry all the tokens in the input from 6.2.2(if 6.2.2 considered as input) or 6.2.3(if 6.2.2 considered as input) removing the stop words.        

