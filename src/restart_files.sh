#!/bin/bash
if [[ ! `pidof -s src/downloader-marketDeribit.py` ]]; then
    invoke-rc.d src/downloader-marketDeribit.py start
fi