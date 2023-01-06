#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249



echo "Moving local  files to remote..."
rclone sync  src/portfolio/deribit b2:MyAppDeribitTradingBAK