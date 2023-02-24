#!/bin/bash
python3 apply_strategies.py

while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
    do 
    rsync -partial -z -e 'ssh -p 22' portfolio/deribit/eth-myTrades-open-recovery-point.pkl MyApp/local_recoveries
    python3  apply_strategies.py
done