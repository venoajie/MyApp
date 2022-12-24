#!/bin/bash
while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
echo AAAA
do  python3 MyApp/src/synchronizing_files.py
done