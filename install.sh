#!/bin/bash

base=$1
prefix=$2

if [ ! "$prefix" ]
then
    echo "No prefix given."
    exit 1
fi

cat ./asc | sed "s#^py=\$#py=/$prefix/lib/asc/main.py#" >./asc-path
install -Dm755 ./asc-path "$base/$prefix/bin/asc"
rm ./asc-path
install -Dm644 ./main.py "$base/$prefix/lib/asc/main.py"
