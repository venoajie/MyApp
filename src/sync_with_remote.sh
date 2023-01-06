#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249

while true; do

    if test -f portfolio/deribit/eth-myTrades-open-recovery-point.pkl;
        then
                echo "file exists"
                echo "Moving local  files to remote..."
                rclone sync  portfolio/deribit/eth-myTrades-open-recovery-point.pkl b2:MyAppTrading
                        
                echo "sleep 30 minutes"
                sleep 30m

        else
                echo "file does not exist"
                rclone copy  portfolio/deribit/eth-myTrades-open-recovery-point.pkl b2:MyAppTrading
                
    fi
done

