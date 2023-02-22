# MyApp

## Current feature list:

- WIP. Will be supported for Deribit/Kraken futures/Binance/Dydx cryptocurrency exchanges. Others coming soon
- works in Python 3.8
- Provide non-hft trading platform that allowed multiple strategy in the same instrument. Could improve the capital efficiency and risk management

## Quickstart:
- install app 
```shell 
git clone https://github.com/venoajie/MyApp.git
``` 
- install dependencies
```shell 
cd MyApp
make install # to download related Linux and Python dependencies
make ram-disk # (optional. Could improve the app speed, but you can easily lose your data due to database persistence)
``` 
- attach .env file in configuration folder
```shell 
cd MyApp/src/configuration
# attach .env file here
``` 
- run app
```shell 
cd MyApp/src
make start # for first time running
``` 

## General troubleshootings:

- Check .env file for any account update
- File crash after applying ram-disk
```shell 
git fetch origin
git reset --hard origin/main
git pull
``` 
reattach .env
