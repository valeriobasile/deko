#!/bin/sh

for method in single weighted
do
for alpha in '0.0' '1.0'
do
for roles in 'false' 'true'
do
for threshold in '0.5' '0.95' '0.99'
do
    echo $method $alpha $roles $threshold
    ./process_clusters.py -c clusters/$method/out_test4_${alpha}_${roles}_${threshold}.txt -i samples/test_sample4.nt > clusters/html/out_test4_${method}_${alpha}_${roles}_${threshold}.html
done
done
done
done
