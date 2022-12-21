#!/bin/bash
while inotifywait -r -e modify,create,delete,move market_data/deribit; do  ls -lh
done