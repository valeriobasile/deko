Clustering code:

1. samples folder has three samples:
	(1) test_sample1.nt is the smallest sample. You can test the code for the first time running on it to get the quick response.
	(2) test_sample2.nt is little bigger sample that has around 160 frame instances. This can be used for quick analysys of the effects of changing the parameters in the code on the sample. This can be used to choose the parameters for the best results.
	(3) complete_sample.nt is the full sample that has around 97,000 frame instances.   

2. Command to see what are the values that parameters can take:
command: python clustering.py -f
output: clustering.py -i <inputfile> -a <alpha value> -t <Frame_similarity_Algo> -e <element_similarity_Algo> -r <true,false> -m <single, complete, average, weighted, centroid, median, ward> -d <distance(greater than 0) range to be considered in same cluster>

3. Terminal command to run the code:
Example: python clustering.py -i samples/test_sample1.nt -m single -a 0.9 -d 1
 
4. Default values set(that are used when no external values for parameters are given) for the  parameters are:
a. input file(-i) : samples/test_sample1.nt
b. alpha(-a) : 0.5
c. Frame similarity Algo(-t) : WUP
d. elemenet similarity Algo(-e): WUP
e. Role consideration(-r) : false
f. clustering method(-m) : weighted
g. clustering distance(-d) : 1

5. Print statements are kept uncommented initially for better understanding of new user while running the code for the first time with smallest sample i.e "test_sample1.nt.". Comment the unwanted print statement in the code for final running on bigger sample to reduce the running time.  


