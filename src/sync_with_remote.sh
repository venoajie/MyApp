#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249

while true; do

    if test -f databases/trdg.bak;
        then
                 echo "file exists"
                echo "Moving local  files to remote..."
                #rclone sync  databases/exchanges/deribit/transactions/eth-myTrades-open-recovery-point.pkl oci:bucket-20230107-0704
                rclone rclone sync databases/trdg.bak remote:/remote-sqlite
                
                echo "sync_with_remote: sleep 30 minutes"
                sleep 60m

        else
                echo "sync_with_remote: file does not exist"
                rclone sync   databases/trdg.bak b2:backup-trading-sqlite
                #rclone sync  databases/exchanges/deribit/transactions/eth-myTrades-open-recovery-point.pkl b2:MyAppTrading
                
    fi
done

