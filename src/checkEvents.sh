#!/bin/bash
@echo "SSSSSSSSSSSSSSSSSSSSSSSSSSSSS"

python3 apply_strategies.py
@echo "WWWWWWWWWWWWWWWWWWWWWWWWWWWW"

rsync -partial -z   databases/exchanges/deribit/transactions/ ~/live/MyApp/local_recoveries/

rsync -partial -z   databases/exchanges/deribit/portfolio/ ~/live/MyApp/local_recoveries/
@echo "XXXXXXXXXXXXXXXXXXXXXXXXX"
while inotifywait -r -e modify,create,delete,move databases/exchanges/deribit/transactions/; 
@echo "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    do 
    @echo "BBBBBBBBBBBBBBBBBBBBBBBBBBBBB"
    rsync -partial -z   databases/exchanges/deribit/transactions/ ~/live/MyApp/local_recoveries/
    @echo "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
    rsync -partial -z   databases/exchanges/deribit/portfolio/ ~/live/MyApp/local_recoveries/
    @echo "DDDDDDDDDDDDDDDDDDDDDDDDDD"
    python3  apply_strategies.py

done