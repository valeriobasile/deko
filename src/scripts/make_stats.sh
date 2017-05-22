#!/bin/sh

for method in single weighted
do
for alpha in '0.0' '1.0'
do
for roles in 'false' 'true'
do
for threshold in '0.5' '0.95' '0.99'
do
    cluster_file=clusters/$method/out_test4_${alpha}_${roles}_${threshold}.txt
    clusters=`cat $cluster_file | cut -d' ' -f2 | sort -u | wc -l`
    echo $method $alpha $roles $threshold $clusters
done
done
done
done
