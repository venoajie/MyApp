#!/bin/bash
python3  synchronizing_files.py
while inotifywait -r -e modify,create,delete,move portfolio/deribit; 
do python3  synchronizing_files.py
sleep 5
/usr/bin/flock -w 0 /tmp/test.lock -c 'python3  synchronizing_files.py'
echo 'AAAAA'
done