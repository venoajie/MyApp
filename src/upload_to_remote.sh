#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249



echo "Moving local  files to remote..."
rclone sync  portfolio/deribit/eth-myTrades-open-recovery-point.pkl b2:MyAppDeribitTradingBAK