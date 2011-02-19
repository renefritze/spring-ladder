#!/bin/bash

cd $(dirname $0)
export PYTHONPATH=$(pwd):$PYTHONPATH
while [ 1 ]; do
	python Main.py
	echo sleeping
	sleep 1
done
