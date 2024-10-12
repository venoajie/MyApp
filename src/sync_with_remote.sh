#!/bin/bash
# https://lovethepenguin.com/linux-check-if-a-file-or-directory-exists-e00cfa672249

while true; do

    if test -f databases/"$(basename $(find $pwd -name "*.bak"))";
        then
                echo "file exists"
                echo "Moving local  files to remote..."
                
                rclone sync databases/"$(basename $(find $pwd -name "*.bak"))" remote:/remote-sqlite

                echo "Delete remaining .bak files..."
                cd databases
                rm *.bak
                cd ..
                
                echo "sleep 15 minutes"
                sleep 15m

        else
                echo "sync_with_remote: file does not exist yet"

                echo "wait file for exist: sleep 10 minutes"
                sleep 10m
                
                
    fi
done

