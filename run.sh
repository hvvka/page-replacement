#!/usr/bin/env bash


TRACES=( 100000 250000 500000 )
FRAMES=( 16 32 64 )


function print_red () {
    echo -e "\033[0;31m${*}\033[0m" >&2
}


# generate data traces
for t in "${TRACES[@]}"
do
    python generator.py --pages $t
    print_red "Trace ${t} generated"
done


# invoke algorithms
for t in "${TRACES[@]}"
do
    for f in "${FRAMES[@]}"
    do
        python vmsim.py --tracefile=data/"${t}".trace --numframes="${f}"
        print_red "Algorithms done for: ${t} trace, ${f} frames"
    done
done
