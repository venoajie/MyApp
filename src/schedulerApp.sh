#!/bin/sh
while [ 1 ]; do
    nohup python3 src/synchronizing_files.py >/dev/null 2>&1 & 
done