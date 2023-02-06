# -*- coding: utf-8 -*-
import src.deribit_get as get_dbt
import asyncio
import pytest
import os
                      
connection_url: str = 'https://www.deribit.com/api/v2/'

def parse_dotenv()->dict:    
    return {'client_id': os.environ.get('client_id'),
            'client_secret': os.environ.get('client_secret')
            }                                                                
                                                  
client_id: str = parse_dotenv() ['client_id']
client_secret: str = parse_dotenv() ['client_secret']

@pytest.mark.asyncio
async def test_get_account_summary():
    account_summary = await (get_dbt.get_account_summary(connection_url,
                                                     client_id,
                                                     client_secret,
                                                     'eth'))
    
    assert list(account_summary) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_positions():
    positions = await (get_dbt.get_positions(connection_url,
                                                     client_id,
                                                     client_secret,
                                                     'eth'))
    
    assert list(positions) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_subaccounts():
    subaccounts = await (get_dbt.get_subaccounts(connection_url,
                                                     client_id,
                                                     client_secret,
                                                     'eth'))
    
    assert list(subaccounts) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_server_time():
    server_time = await (get_dbt.get_server_time(connection_url))
    
    assert list(server_time) ==  ['jsonrpc', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_currencies():
    currencies = await (get_dbt.get_currencies(connection_url))
    
    assert list(currencies) ==  ['jsonrpc', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_index():
    get_index = await (get_dbt.get_index(connection_url,'eth'))
    
    assert list(get_index) ==  ['jsonrpc', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_get_instruments():
    get_instruments = await (get_dbt.get_instruments(connection_url, 'eth'))
    
    assert   list(get_instruments) ==  ['jsonrpc', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']