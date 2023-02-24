#!/bin/bash
python3 apply_strategies.py
rsync -partial -z   portfolio/deribit/ ~/live/MyApp/local_recoveries/

while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
    do 
    
    rsync -partial -z   portfolio/deribit/ ~/live/MyApp/local_recoveries/
    python3  apply_strategies.py

done