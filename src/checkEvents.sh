#!/bin/bash
python3 apply_strategies.py
rsync -partial -z   databases/transactions/deribit/ ~/live/MyApp/local_recoveries/
rsync -partial -z   databases/portfolio/deribit/ ~/live/MyApp/local_recoveries/

while inotifywait -r -e modify,create,delete,move databases/transactions/deribit; 
    do 
    
    rsync -partial -z   databases/transactions/deribit/ ~/live/MyApp/local_recoveries/
    rsync -partial -z   databases/portfolio/deribit/ ~/live/MyApp/local_recoveries/
    python3  apply_strategies.py

done