#!/bin/bash

cd $(dirname $0)
export PYTHONPATH=$(pwd):$(pwd)/encutils:$(pwd)/cssutils:$(pwd)/svg.charts:$PYTHONPATH
while [ 1 ] ; do
	nice python main.py # | tee out.log 
	sleep 2
done
