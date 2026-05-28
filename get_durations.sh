#!/bin/bash

get_durations() {
    ffprobe -hide_banner -loglevel quiet -show_streams $1 | grep duration= | cut -d = -f 2
}

all_durations() {
    local expr='define round(a) {
        scale = 0;
        return a/1 + ((a - a/1) >= 0.5);
    }
    '

    for k in `cat audios.csv | cut -d , -f 3 | tail -n +2 | sed -e 's/"//g'`
    do
        l=`get_durations $k`

        hrs=`echo "$expr round($l)/3600;" | bc`
        mins=`echo "$expr (round($l)/60)%60;" | bc`
        secs=`echo "$expr round($l)%60;" | bc`

        printf "%02d:%02d:%02d\n" $hrs $mins $secs
    done
}


cd testing-audios

# I honestly don't know why but ok
paste -d, audios.csv <(all_durations | cat <(echo "DURATION") -) > audios_next.csv

cat audios_next.csv > audios.csv
