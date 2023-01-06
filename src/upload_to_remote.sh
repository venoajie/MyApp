#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249

if test -f portfolio/deribit/eth-myTrades-open-recovery-point.pkl;
then
        echo "file exists"
else
        echo "file does not exist"
fi


echo "Moving local  files to remote..."
rclone sync  portfolio/deribit/eth-myTrades-open-recovery-point.pkl b2:MyAppDeribitTradingBAK
