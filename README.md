Default Knowledge about Objects
===============================

DeKO is a repository of default knowledge about common object.

DeKO is built by parsing natural language text with [KNEWS](), extraccting instances of frames from the text, and the clustering the frames.

Frame clustering
----------------

Clustering is based on some kind of distance (or conversely, similarity) measure.
For DeKO, we defined a similarity measure between frame isntances. It is implemented in the script framesimilarity.py.

Instructions:
1. script: Code works for any of the following scripts, given as partially or fully.
'src.py -a <alpha value> -t <Frame_similarity_Algo> -e <element_similarity_Algo> -r <true,false> <inputfile1> <inputfile2>'

'src.py --alpha <alpha value> --F_Sim_Algo <Frame_sim_Algo> --E_sim_Algo <element_similarity_Algo> --role <true,false> <inputfile1> <inputfile2>'

Parameters values:
1. -a or --alpha :
default : 0.5

2. -t or --F_Sim_Algo :
default : WUP

3. -e or --E_sim_Algo :
default : WUP

4. -r or --role :
default : false

The input files are two text files containing RDF triples, defining one frame instance each.

*Test input files are run from the folder named "frame_files"
*Any similarity calculating algorithm can be implemented instead of WUP for either between frame_types or frame_elements. Just add the module and call that similarity. Comments are mentioned in the code at place where new algo can be called.
*Necessary comments are mentioned in the code.
*For analysing results at each level of calculation, uncomment the print statements and run.
*Data structures like list, dictionary and tuples are used so that the code can be easily used for multiple frames if require at some point.
