#!/bin/bash
while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
echo AAAA
pkill synchronizing_files.py
do  python3  synchronizing_files.py
done