#!/bin/bash
while inotifywait -r -e modify,create,delete,move portfolio/deribit; do  python3 src/sycnhronizing_files.py
done