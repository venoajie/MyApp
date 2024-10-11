#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249

while true; do


    if test -f databases/"$(basename $(find $pwd -name "*.bak"))";
        then
                echo "file exists"
                echo "Moving local  files to remote..."
                #rclone sync  databases/exchanges/deribit/transactions/eth-myTrades-open-recovery-point.pkl oci:bucket-20230107-0704
                
                sleep 5s

                #rclone sync --include databases/*.bak remote:/remote-sqlite
                cd databases
                rm *.bak
                cd ..
                
                echo "sync_with_remote: sleep 15 minutes"
                sleep 15m

        else
                echo "sync_with_remote: file does not exist"
                #rclone sync --include databases/*.bak remote:/remote-sqlite

                #clone sync databases  b2:/remote-sqlite  --include *.{bak}
                echo "wait file for exist: sleep 5 minutes"
                sleep 5m
                
                #rclone sync  databases/exchanges/deribit/transactions/eth-myTrades-open-recovery-point.pkl b2:MyAppTrading
                
    fi
done

