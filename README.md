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
make ram-disk # (optional, resizing ram disk to 2 GB. Could improve the app speed, but you can easily lose your data due to database persistence)
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

- Check .env file for any account update/ram-disk size change
- File crash after resizing ram-disk
```shell 
git fetch origin
git reset --hard origin/main
git pull
``` 

```shell 
cd MyApp/src/configuration
# re-attach .env file here
``` 
- Fail to install Python dependecies (specific for Ubuntu 20). Downgrade setup tools:
```shell 
pip3 install --upgrade --user setuptools==58.3.0
``` 
