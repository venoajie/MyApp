[![Python application](https://github.com/venoajie/MyApp/actions/workflows/python-app.yml/badge.svg)](https://github.com/venoajie/MyApp/actions/workflows/python-app.yml)
[![Format code](https://github.com/venoajie/MyApp/actions/workflows/format.yml/badge.svg)](https://github.com/venoajie/MyApp/actions/workflows/format.yml)
[![Unit tests](https://github.com/venoajie/MyApp/actions/workflows/coverage.yml/badge.svg)](https://github.com/venoajie/MyApp/actions/workflows/coverage.yml)
![code coverage](https://raw.githubusercontent.com/USER/REPO/coverage/coverage.svg?raw=true)

# MyApp
#### Provide non-hft trading platform that allowed multiple strategy in the same instrument. Could improve the capital efficiency and risk management.

#### Supported exchanges: Deribit. Others coming soon

#### WIP. Tested in Python 3.8 and Ubuntu 20.04 environment

## Current feature list:
- [x] Automatic **hedging** for equity balances in crypto spot
- [x] Back up database to cloud and local
- [x] Send automatic order based on pre-defined manual target

## Transaction flow:
- Fetch both market and exchange data through websocket and temporary save them in pickle format
    Why pickle: it is easy. Data can be saved as is to its format without further modification. Also, it is fast.
- Modify market data for further analysis
- Check the balance in cryto currency. Check whether they have properly hedged
- Determine parameters for risk management at configuration files (especially, max risk per transaction as the basis for position sizing)
- Frequently check market condition and current asset position. Send/cancel order based on them
- Frequently: check current position based on time (every x seconds using sleep function as well as scheduler) and events (by captured any changes taken place at balance/position using rsync)
- Send transaction update to telegram
- Finally, back up data to cloud and other folder using rclone every x hours

## Quick start:
- install app 
```shell 
git clone https://github.com/venoajie/MyApp.git
``` 
- install dependencies
```shell 
cd MyApp
make install # to download related Linux and Python dependencies
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

## File structure:

- general folder structure

    ```
    .
    ├── src
    │   ├── configuration
    │   ├── databases
    │       ├── trading.sqlite3
    │       ├── exchanges
    │       ├── market
    │   ├── market_data
    │       ├── get_market_data.py
    │   ├── market_understanding
    │       ├── futures_analysis.py
    │   ├── risk_management
    │       ├── position_sizing.py
    │   ├── strategies
    │   ├── transaction_management
    │   ├── utilities
    │   ├── capture_exch_data_fr_deribit.py
    │   ├── capture_market_data_fr_deribit.py
    │   ├── checkEvents.sh
    │   ├── deribit_get.py
    │   ├── fetch_and_save_market_data.py
    │   ├── Makefile
    ├── tests
    ├── Makefile
    └── requirements.txt
    ```
