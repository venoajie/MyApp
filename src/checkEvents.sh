#!/bin/bash
python3 apply_strategies.py
echo 'aaaaaaaaaaaaaaaaaa'
rsync -partial -z   databases/exchanges/deribit/transactions/ ~/live/MyApp/local_recoveries/
echo 'bbbbbbbbbbbbbb'
rsync -partial -z   databases/exchanges/deribit/portfolio/ ~/live/MyApp/local_recoveries/
echo 'ccccccccccccccccc'

while inotifywait -r -e modify,create,delete,move databases/exchanges/deribit/transactions; 
    do 
    echo 'dddddddddddddddddddddd'
    
    rsync -partial -z   databases/exchanges/deribit/transactions/ ~/live/MyApp/local_recoveries/
    rsync -partial -z   databases/exchanges/deribit/portfolio/ ~/live/MyApp/local_recoveries/
    python3  apply_strategies.py

done