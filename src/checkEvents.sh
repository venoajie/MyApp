#!/bin/bash
python3  synchronizing_files.py
python3 apply_strategies.py

while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
    do 
    python3  synchronizing_files.py
    python3  apply_strategies.py
done