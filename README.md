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
- run make file
```shell 
cd MyApp
make install # to download related Linux and Python dependencies
make ram-disk # (optional. Could improve tha app speed, but you can easily lose your data due to database persistence)
``` 
- attach .env file
```shell 
cd MyApp/src/configuration
# attach .env file here
``` 

## General troubleshootings:

- Check .env file for any account update

