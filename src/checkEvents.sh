#!/bin/bash

python3 apply_strategies.py

rsync -partial -z   databases/exchanges/deribit/transactions/ ~/live/MyApp/local_recoveries/

rsync -partial -z   databases/exchanges/deribit/portfolio/ ~/live/MyApp/local_recoveries/

while inotifywait -r -e modify,create,delete,move databases/exchanges/deribit/portfolio/eth-portfolio.pkl; 

    do 

    python3  apply_strategies.py

    rsync -partial -z   databases/exchanges/deribit/transactions/ ~/live/MyApp/local_recoveries/

    rsync -partial -z   databases/exchanges/deribit/portfolio/ ~/live/MyApp/local_recoveries/


done