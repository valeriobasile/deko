                               SemEval 2017 Task 1

                         Semantic Textual Similarity (STS)
                                   Trial Data

This package contains the trial data for the multilingual semantic textual 
similarity (STS) shared task, SemEval 2017 Task 1.

The following files are provided:

 00-README.txt                             This file.
 LICENSE.txt                               Licensing information for the source
                                           material of the trial data pairs.
 correlation.pl                            Evaluation script for a single 
                                           dataset.
 correct-output.pl                         System output validation script.
 STS.input.[lang]-[lang].trial.txt         Tab separated sample input file with
                                           either monolingual or cross-lingual
                                           sentence pairs.
 STS.gs.trial.txt                          Gold standard annotations.
 STS.output.trial.txt                      Sample system output.

Languages [lang]: ar, es, en

Introduction
------------

This README describes the trial data for the 2017 multilingual STS shared task. 

This year's shared task has 5 tracks:

  Track 0 - Primary: Combined evaluation of all monolingual and cross-lingual 
  language pairings explored by the 2017 task: ar-ar, ar-en, es-en, and es-es.

  Track 1 - Arabic-Arabic: Evaluation over ar-ar pairs.

  Track 2 - Arabic-English: Evaluation over ar-en pairs.

  Track 3 - Spanish-Spanish: Evaluation over es-es pairs

  Track 4 - Spanish-English: Evaluation over es-en pairs.

For all language pairings, systems will be provided with two sentence length 
snippets of text, s1 and s2, and will be asked to compute the similarity of the 
underlying semantics of the pair and return a continuous valued similarity 
score.

The cross-lingual language pairings (ar-en, es-en) only differ from the 
monolingual language pairings (ar-ar, es-es) in that the two text snippets in 
each pair are in different languages. The inclusion of cross-lingual STS pairs 
follows a successful pilot in 2016 that paired English and Spanish sentences. 

Depending on the model being used to compute the similarity scores the
cross-lingual pairings may present different degrees of difficulty in adapting
the model to handle the cross-lingual pairs. 

Participants are encouraged to review the successful approaches to monolingual 
and cross-lingual STS from prior years of the STS shared task (Agirre et al. 
2016; Agirre et al. 2015; Agirre et al. 2014; Agirre et al. 2013; Agirre et al. 
2012)  


Trial Data
----------

The 2017 trial data is drawn from English monolingual data collected for the 
2016 English STS task. The English STS sentence pairs were sampled at random 
and the sentences within each pair are translated by a fluent human speaker to 
Arabic and Spanish. The translations are then used to construct both the 
cross-lingual and monolingual trial pairs. For the monolingual trial pairs, 
both sentences in a pair are replaced by their translations into either Arabic 
or Spanish. For the cross-lingual trial pairs, only a single sentence is 
replaced with its translation leaving the other sentence in the pair in its 
original English. For reference, the original monolingual English pairs are 
also included in this package.

The data is balanced across STS scores, with 4 examples per each STS level per 
language. The test data will also be approximately balanced across STS scores.

Possible Methods
----------------

Refer to sections 6.4.1 and 6.5.1 of the 2016 STS task summary paper for an 
overview of state-of-the-art approaches to monolingual and cross-lingual STS:
  
  Eneko Agirre, Carmen Banea, Daniel Cer, Mona Diab, Aitor Gonzalez-Agirre,
  Rada Mihalcea, German Rigau, Janyce Wiebe. SemEval-2016 Task 1: Semantic
  Textual Similarity, Monolingual and Cross-Lingual Evaluation. In Proceedings
  of SemEval 2016.

  http://anthology.aclweb.org/S/S16/S16-1081.pdf

Input format
------------

The input file consists of paired text snippets with one pair per line with each
line also containing information on where the snippets in the pair were sourced.

The following tab separated fields appear on each line:

 * <1st text snippet>
 * <2nd text snippet>
 * <1st snippet data source>
 * <2nd snippet data source>

File: STS.input.[lang]-[lang].trial.txt

Lang: ar, es, en


Gold Standard
-------------

The gold standard file contains a score between 0 and 5 for each pair of
statements, with the interpretations found below. Examples are given with 
English-Spanish pairs:

(5) The two sentences are completely equivalent, as they mean the same
    thing.

       El pájaro se está bañando en el lavabo.
       Birdie is washing itself in the water basin.

(4) The two sentences are mostly equivalent, but some unimportant
    details differ.

       En mayo de 2010, las tropas intentaron invadir Kabul.
       The US army invaded Kabul on May 7th last year, 2010.

(3) The two sentences are roughly equivalent, but some important
    information differs or is missing.

       John dijo que él es considerado como testigo, y no como sospechoso.
       "He is not a suspect anymore." John said.

(2) The two sentences are not equivalent, but share some details.

       Ellos volaron del nido en grupos.
       They flew into the nest together.

(1) The two sentences are not equivalent, but are on the same topic.

       La mujer está tocando el violín.
       The young lady enjoys listening to the guitar.

(0) The two sentences are on different topics.

       Al amanecer, Juan se fue a montar a caballo con un grupo de amigos.
       Sunrise at dawn is a magnificent view to take in if you wake up
       early enough for it.

The gold standard file format consists of one single field per line:

      - a number between 0 and 5

File: STS.gs.trial.txt


Answer format
--------------

The answer format is identical to the gold standard format. Each line should
have one number corresponding to your system's predicted STS score for a pair:

      - a number between 0 and 5 (the computed similarity score)

The output file must conform to the above specification. Incorrectly formatted
files will be automatically removed from the evaluation. You can verify that
your answer files are in the proper format using the following script:

      $ ./correct-output.pl STS.output.SMT.txt
      Output file is OK!

In addition to reporting problems and an overall final status message on
standard error, the script also returns 0 if and only if the provided file is
correctly formatted.

File: STS.output.trial.txt


Scoring
-------

The official score is based on weighted Pearson correlation.

The following script returns the correlation for individual pairs:


       $ ./correlation.pl \
          STS.gs.trial.txt \
          STS.output.trial.txt
       Pearson: 0.84871


Participation in the task
-------------------------

Participants will be allowed to submit at most three runs using minor variants
of a single system.

However, participants with two or more substantively different models or
approaches will be allowed to submit up to five different systems. If you plan
on submitting more than three systems please check with the task organizers
first, to see if the methods being used are different enough to warrant more
than three submissions.


Resources
---------

Task website: http://alt.qcri.org/semeval2017/task1/

Semantic Textual Similarity Wiki:

       http://ixa2.si.ehu.es/stswiki/index.php/Main_Page

We highly recommend that potential participants join the task mailing list:

     http://groups.google.com/group/STS-semeval


Organizers (alpha. order)
----------
 
Eneko Agirre (University of the Basque Country)
Mona Diab (George Washington University)
Daniel Cer (Google)
Lucia Specia (University of Sheffield)


Acknowledgements
----------------

The organizers would like to thank Abdelati Hawwari for his help in preparing 
the Arabic data.

Revision History
----------------
Sept 21st, 2016 - First release (this version)

