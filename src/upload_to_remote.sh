#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249

        
fi

while true; do

if test -f portfolio/deribit/eth-myTrades-open-recovery-point.pkl;
    then
            echo "file exists"
            echo "Moving local  files to remote..."
            rclone sync  portfolio/deribit/eth-myTrades-open-recovery-point.pkl b2:MyAppDeribitTradingBAK

    else
            echo "file does not exist"
            
            
        fi
    echo "sleep 10 seconds"
    sleep 10
done


