# -*- coding: utf-8 -*-
import src.deribit_get as get_dbt
import asyncio
import pytest
                      
connection_url: str = 'https://www.deribit.com/api/v2/'
sub_account = 'deribit-147691'
    
def parse_dotenv(sub_account)->dict:    
    from configuration import config
    return config.main_dotenv (sub_account)                                                         
             
client_id: str = parse_dotenv(sub_account) ['client_id']
client_secret: str = parse_dotenv(sub_account) ['client_secret']
print (client_id)
print (client_secret)

@pytest.mark.asyncio
async def test_get_user_trades_by_instrument():
    user_trades_by_instrument = await get_dbt.get_user_trades_by_instrument(connection_url,
                                                                            client_id,
                                                                            client_secret,
                                                                            'eth-perpetual'
                                                                            )    
    assert (user_trades_by_instrument) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    assert list(user_trades_by_instrument) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    

@pytest.mark.asyncio
async def test_get_open_orders_byInstruments():
    open_orders_byInstruments = await (get_dbt.get_open_orders_byInstruments(connection_url,
                                                     client_id,
                                                     client_secret,
                                                     'eth-perpetual',
                                                     'all'))
    
    assert list(open_orders_byInstruments) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    

@pytest.mark.asyncio
async def test_get_order_history_by_instrument():
    order_history_by_instrument = await (get_dbt.get_order_history_by_instrument(connection_url,
                                                     client_id,
                                                     client_secret,
                                                     'eth-perpetual'))
    
    assert list(order_history_by_instrument) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_open_orders_byCurrency():
    open_orders_byCurrency = await (get_dbt.get_open_orders_byCurrency(connection_url,
                                                     client_id,
                                                     client_secret,
                                                     'eth'))
    
    assert list(open_orders_byCurrency) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
@pytest.mark.asyncio
async def test_get_user_trades_by_currency():
    user_trades_by_currency = await (get_dbt.get_user_trades_by_currency(connection_url,
                                                     client_id,
                                                     client_secret,
                                                     'eth'))
    
    assert list(user_trades_by_currency) ==  ['jsonrpc', 'id', 'result', 'usIn', 'usOut', 'usDiff', 'testnet']
    
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
    
@pytest.mark.asyncio
async def test_ohlc():
    
    resolution= 15
    qty_candles = 100
    ohlc = await (get_dbt.get_ohlc(connection_url, 
                                   'eth-perpetual', 
                                   resolution,
                                   qty_candles)
                  )
    
    assert   list(ohlc) == ['usOut', 'usIn', 'usDiff', 'testnet', 'result', 'jsonrpc']
    
@pytest.mark.asyncio
async def test_get_open_interest_aggregated_ohlc():
    
    resolution= 'm5'
    connection_url: str = 'https://open-api.coinglass.com/public/v2/'
    
    ohlc = await (get_dbt.get_open_interest_aggregated_ohlc(connection_url, 
                                   'eth-perpetual', 
                                   resolution)
                  )
    
    assert   list(ohlc) == ['code', 'msg', 'success'] 
    
    
@pytest.mark.asyncio
async def test_get_open_interest_historical():
    
    resolution= 'm5'
    connection_url: str = 'https://open-api.coinglass.com/public/v2/'
    
    ohlc = await (get_dbt.get_open_interest_historical(connection_url, 
                                   'eth', 
                                   resolution)
                  )
    
    assert   list(ohlc) == ['code', 'msg', 'success'] 
    
@pytest.mark.asyncio
async def test_get_open_interest_symbol():
    
    connection_url: str = 'https://open-api.coinglass.com/public/v2/'
    
    open_interest = await (get_dbt.get_open_interest_symbol(connection_url, 
                                   'eth')
                  )
    
    assert   list(open_interest) == ['code', 'msg', 'success'] 
    
@pytest.mark.asyncio
async def test_telegram_bot_sendtext():
    bot_message = 'test with purpose-general error'
    purpose = 'general_error'
    
    result = await get_dbt.telegram_bot_sendtext (bot_message,
                                 purpose
                                 )
    
    assert   list(result) == ['ok', 'result'] 
    
    bot_message = 'test with None purpose'

    result = await get_dbt.telegram_bot_sendtext (bot_message)
    
    assert   list(result) == ['ok', 'result'] 
        
    bot_message = 'test with purpose-failed order'
    purpose = 'failed_order'

    result = await get_dbt.telegram_bot_sendtext (bot_message,
                                 purpose
                                 )
    assert   list(result) == ['ok', 'result'] 