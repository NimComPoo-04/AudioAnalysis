#!/bin/bash

mkdir -p testing-audios
cd testing-audios

# Get the names folks
if [ ! -f audios.csv ]
then
    touch example
    for page in `seq 10`
    do
        curl -L "https://freesound.org/search/?q=traffic+horn&s=Automatic+by+relevance&page=$page"\
            | grep -e '".*cdn.freesound.org.*\.mp3"'\
            | cut -d = -f 2 >> example
    done

    n=`cat example | wc -l`
    paste -d , <(seq $n) example <(cat example | cut -d / -f 6 | sed -e 's/^/"/g') | cat <(echo "ID,URL,FILE") - > audios.csv

    rm example
fi

for lines in `tail -n +2 audios.csv`
do
    url=`echo $lines | cut -d , -f 2 | sed -e 's/"//g'`
    file=`echo $lines | cut -d , -f 3 | sed -e 's/"//g'`

    if [ ! -f $file ]
    then
        curl -L $url -o $file
    fi
done
