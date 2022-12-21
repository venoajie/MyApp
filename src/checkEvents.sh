#!/bin/bash
while inotifywait -r -e modify,create,delete,move portfolio/deribit; do  ls -lh
done