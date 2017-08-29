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
echo $ftsim $fesim $agg $r $a `sts2017-trial-data/correlation.pl STS.gs.track5.en-en.txt results/$ftsim-$fesim-$agg-$a-$r.txt `
done
done
done
done
done
