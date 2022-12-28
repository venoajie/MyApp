#!/bin/bash
do python3  synchronizing_files.py
while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
do python3  synchronizing_files.py
done