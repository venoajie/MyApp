#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
import aioschedule as schedule
import time
import aiohttp
from loguru import logger as log

from strategies.config_strategies import (hedging_spot_attributes,preferred_spot_currencies,paramaters_to_balancing_transactions,strategies)

sub_accounts= [{'positions': [
    {'estimated_liquidation_price': None, 'size_currency': -0.00216529, 'realized_funding': 5e-08, 'total_profit_loss': -7.7698e-05, 
     'realized_profit_loss': 4.5e-08, 'floating_profit_loss': -7.2446e-05, 'leverage': 50, 'average_price': 57958.4, 'delta': -0.00216529, 
     'interest_value': 0.010018865505920705, 'mark_price': 60038.16, 'settlement_price': 58094.43, 'instrument_name': 'BTC-PERPETUAL', 
     'open_orders_margin': 0.000192753, 'initial_margin': 4.3306e-05, 'maintenance_margin': 2.1653e-05, 'index_price': 60013.44, 'direction': 'sell', 'kind': 'future', 'size': -130.0}], 
                     'open_orders': [{'is_liquidation': False, 'risk_reducing': False, 'order_type': 'limit', 'creation_timestamp': 1726228258653, 
                                      'order_state': 'open', 'reject_post_only': False, 'contracts': 10.0, 'average_price': 0.0, 'reduce_only': False,
                                      'last_update_timestamp': 1726228258653, 'filled_amount': 0.0, 'post_only': True, 'replaced': False, 'mmp': False,
                                      'order_id': '77544700787', 'web': False, 'api': True, 'instrument_name': 'BTC-PERPETUAL', 'max_show': 100.0, 'time_in_force': 'good_til_cancelled', 'direction': 'sell', 'amount': 100.0, 'price': 65000.0, 'label': 'customShort-open-1726228258298'}], 'uid': 148510}]

log.warning ( sub_accounts[0]["open_orders"])
