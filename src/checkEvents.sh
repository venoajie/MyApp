#!/bin/bash
while inotifywait -r -e modify,create,delete,move portfolio/deribit; do  python3 sycnhronizing_files.py
done