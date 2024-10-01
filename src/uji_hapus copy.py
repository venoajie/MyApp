
from utilities.system_tools import (
    provide_path_for_file)
import os, tomli


data=  [{'tick_size_steps': [], 
         'quote_currency': 'USD', 'min_trade_amount': 10.0, 'counter_currency': 'USD', 'settlement_currency': 'BTC', 
         'block_trade_min_trade_amount': 200000, 'block_trade_commission': 0.00025, 'max_liquidation_commission': 0.0075, 
         'max_leverage': 25, 'future_type': 'reversed', 'creation_timestamp': 1726819213000, 'settlement_period': 'week',
         'instrument_id': 370613, 'base_currency': 'BTC', 'block_trade_tick_size': 0.01, 'tick_size': 2.5, 'contract_size': 10.0, 'is_active': True, 
         'expiration_timestamp': 1728028800000, 'instrument_type': 'reversed', 'taker_commission': 0.0005, 'maker_commission': -0.0001, 
         'instrument_name': 'BTC-4OCT24', 'kind': 'future', 'rfq': False, 'price_index': 'btc_usd'}, {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 10.0, 'counter_currency': 'USD', 'settlement_currency': 'BTC', 'block_trade_min_trade_amount': 200000, 'block_trade_commission': 0.00025, 'max_liquidation_commission': 0.0075, 'max_leverage': 25, 'future_type': 'reversed', 'creation_timestamp': 1727424018000, 'settlement_period': 'week', 'instrument_id': 373193, 'base_currency': 'BTC', 'block_trade_tick_size': 0.01, 'tick_size': 2.5, 'contract_size': 10.0, 'is_active': True, 'expiration_timestamp': 1728633600000, 'instrument_type': 'reversed', 'taker_commission': 0.0005, 'maker_commission': -0.0001, 'instrument_name': 'BTC-11OCT24', 'kind': 'future', 'rfq': False, 'price_index': 'btc_usd'}, {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 10.0, 'counter_currency': 'USD', 'settlement_currency': 'BTC', 'block_trade_min_trade_amount': 200000, 'block_trade_commission': 0.00025, 'max_liquidation_commission': 0.0075, 'max_leverage': 50, 'future_type': 'reversed', 'creation_timestamp': 1534242287000, 'settlement_period': 'perpetual', 'instrument_id': 210838, 'base_currency': 'BTC', 'block_trade_tick_size': 0.01, 'tick_size': 0.5, 'contract_size': 10.0, 'is_active': True, 'expiration_timestamp': 32503708800000, 'instrument_type': 'reversed', 'taker_commission': 0.0005, 'maker_commission': 0.0, 'instrument_name': 'BTC-PERPETUAL', 'kind': 'future', 'rfq': False, 'price_index': 'btc_usd'}, {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 1, 'counter_currency': 'USD', 'settlement_currency': 'ETH', 'block_trade_min_trade_amount': 100000, 'block_trade_commission': 0.00025, 'max_liquidation_commission': 0.009, 'max_leverage': 25, 'future_type': 'reversed', 'creation_timestamp': 1726819212000, 'settlement_period': 'week', 'instrument_id': 370612, 'base_currency': 'ETH', 'block_trade_tick_size': 0.01, 'tick_size': 0.25, 'contract_size': 1, 'is_active': True, 'expiration_timestamp': 1728028800000, 'instrument_type': 'reversed', 'taker_commission': 0.0005, 'maker_commission': -0.0001, 'instrument_name': 'ETH-4OCT24', 'kind': 'future', 'rfq': False, 'price_index': 'eth_usd'}, {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 1, 'counter_currency': 'USD', 'settlement_currency': 'ETH', 'block_trade_min_trade_amount': 100000, 'block_trade_commission': 0.00025, 'max_liquidation_commission': 0.009, 'max_leverage': 25, 'future_type': 'reversed', 'creation_timestamp': 1727424017000, 'settlement_period': 'week', 'instrument_id': 373086, 'base_currency': 'ETH', 'block_trade_tick_size': 0.01, 'tick_size': 0.25, 'contract_size': 1, 'is_active': True, 'expiration_timestamp': 1728633600000, 'instrument_type': 'reversed', 'taker_commission': 0.0005, 'maker_commission': -0.0001, 'instrument_name': 'ETH-11OCT24', 'kind': 'future', 'rfq': False, 'price_index': 'eth_usd'}, {'tick_size_steps': [], 'quote_currency': 'USD', 'min_trade_amount': 1, 'counter_currency': 'USD', 'settlement_currency': 'ETH', 'block_trade_min_trade_amount': 100000, 'block_trade_commission': 0.00025, 'max_liquidation_commission': 0.009, 'max_leverage': 50, 'future_type': 'reversed', 'creation_timestamp': 1552568454000, 'settlement_period': 'perpetual', 'instrument_id': 210760, 'base_currency': 'ETH', 'block_trade_tick_size': 0.01, 'tick_size': 0.05, 'contract_size': 1, 'is_active': True, 'expiration_timestamp': 32503708800000, 'instrument_type': 'reversed', 'taker_commission': 0.0005, 'maker_commission': 0.0, 'instrument_name': 'ETH-PERPETUAL', 'kind': 'future', 'rfq': False, 'price_index': 'eth_usd'}]


def get_config(file_name: str) -> list:
    """ """
    config_path = provide_path_for_file (file_name)
    
    try:
        if os.path.exists(config_path):
            with open(config_path, "rb") as handle:
                read= tomli.load(handle)
                return read
    except:
        return []


file_toml =  "config_strategies.toml"
print (get_config(file_toml))
