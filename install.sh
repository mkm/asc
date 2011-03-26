#!/bin/bash

prefix=$1

if [ ! "$prefix" ]
then
    echo "No prefix given."
    exit 1
fi

cat ./asc | sed "s#^py=\$#py=$prefix/lib/asc/main.py#" >./asc-path
install -Dm755 ./asc-path "$prefix/bin/asc"
rm ./asc-path
install -Dm644 ./main.py "$prefix/lib/asc/main.py"
