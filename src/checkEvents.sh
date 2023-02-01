#!/bin/bash
python3 apply_strategies.py

while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
    do 
    python3  apply_strategies.py
done