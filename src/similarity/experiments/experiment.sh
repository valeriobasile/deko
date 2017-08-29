#!/bin/sh

for ftsim in occ dist
do
for fesim in dist
do
for agg in max avg
do
for r in false true
do
for a in `seq 0.0 0.1 1.0`
do
../../sentence_similarity.py -l filelist_babelfy -a $a -r $r -t $ftsim -e $fesim -g $agg > results/$ftsim-$fesim-$agg-$a-$r.txt
done
done
done
done
done
