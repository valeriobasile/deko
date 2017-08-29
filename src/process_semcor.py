#!/usr/bin/env python

with open('/home/vbasile/Downloads/semcor3.0/semcor3.0.xml') as f:
    for line in f:
        if line.startswith("<context "):
            context = line.rstrip().split(' ')[1].replace('filename=', '')
        elif line.startswith("<p "):
            paragraph = line.rstrip().replace('<p pnum=', '').replace('>', '')
        elif line.startswith("<s "):
            sentence = line.rstrip().replace('<s snum=', '').replace('>', '')
        elif line.startswith("<wf cmd=done "):
            fields = line.rstrip().split(' ')
            lemma = None
            for field in fields:
                if field.startswith('lemma='):
                    lemma = field.replace('lemma=', '')

            sense = None
            for field in fields:
                if field.startswith('wnsn='):
                    sense = field.replace('wnsn=', '')

            if lemma and sense:
                print "{0}-{1}-{2}\t{3}\t{4}".format(context, paragraph, sentence, lemma, sense)
