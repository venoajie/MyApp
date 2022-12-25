#!/bin/bash
while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
echo AAAA
do pkill synchronizing_files.py python3  synchronizing_files.py
done