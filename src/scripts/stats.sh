#!/bin/sh

ntriple_file=$1
triples=`cat $ntriple_file | wc -l`
frame_instances=`cat $ntriple_file | cut -d' ' -f1 | sort -u | wc -l`
frame_types=`cat $ntriple_file | grep "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" | cut -d' ' -f3 | sort -u | wc -l`

echo -e "$ntriple_file\t$triples\t$frame_instances\t$frame_types"
