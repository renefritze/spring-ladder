#!/bin/bash
cd $(dirname $0)
export PYTHONPATH=$(pwd):$PYTHONPATH
nice python main.py
