from utilities import string_modification, number_modification, pickling, system_tools
from configuration import config
    #from loguru import logger as log
my_trades_open = [{'trade_seq': 118020115, 'trade_id': 'ETH-160804604', 'timestamp': 1677059533908, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1640.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31873685113', 'mmp': False, 'matching_id': None, 'mark_price': 1640.88, 'liquidity': 'M', 'label': 'test-open-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1641.03, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 78.0}, {
        "trade_seq": 118647438,
        "trade_id": "ETH-161557067",
        "timestamp": 1677807144369,
        "tick_direction": 2,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.00039974,
        "price": 1535,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-31941707258",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1544.41,
        "liquidity": "M",
        "label": "test-closed-1677059533",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1552.18,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "buy",
        "api": True,
        "amount": 10
      },
      {
        "trade_seq": 118697746,
        "trade_id": "ETH-161622575",
        "timestamp": 1677835222867,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1569.65,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32042276354",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1569.81,
        "liquidity": "M",
        "label": "hedgingSpot-open-1677835222468",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1570.19,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 7
      },
      {
        "trade_seq": 118646176,
        "trade_id": "ETH-161555549",
        "timestamp": 1677807136264,
        "tick_direction": 3,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0.0003367,
        "price": 1550,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-31941709815",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1555.56,
        "liquidity": "M",
        "label": "test-closed-1677059533",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1560.48,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "buy",
        "api": True,
        "amount": 10
      },
                  
                  
                  {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 7.0}, {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 11.0}, {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118305997, 'trade_id': 'ETH-161151946', 'timestamp': 1677379636994, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1599.6, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31944078044', 'mmp': False, 'matching_id': None, 'mark_price': 1599.64, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677379624', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1599.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118327634, 'trade_id': 'ETH-161178533', 'timestamp': 1677436936464, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1622.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31951464881', 'mmp': False, 'matching_id': None, 'mark_price': 1621.27, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677436932', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1620.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118342537, 'trade_id': 'ETH-161197087', 'timestamp': 1677452774256, 'tick_direction': 0, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1642.85, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31955055472', 'mmp': False, 'matching_id': None, 'mark_price': 1642.28, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677452758', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1642.25, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, 
                  
                  
                  {'trade_seq': 118355869, 'trade_id': 'ETH-161212758', 'timestamp': 1677474758759, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -0.00011743, 'price': 1635.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31958514035', 'mmp': False, 'matching_id': None, 'mark_price': 1635.17, 'liquidity': 'M', 'label': 'supplyDemandLong60-open-1677473096934', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1635.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 9.0},
      {
        "trade_seq": 118554841,
        "trade_id": "ETH-161447719",
        "timestamp": 1677716308851,
        "tick_direction": 1,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1675,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-31958514019",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1675.06,
        "liquidity": "M",
        "label": "supplyDemandShort60-open-1677473096",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1674.09,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 8
      },
     
      {
        "trade_seq": 118698584,
        "trade_id": "ETH-161624004",
        "timestamp": 1677836968025,
        "tick_direction": 3,
        "state": "filled",
        "self_trade": False,
        "risk_reducing": False,
        "reduce_only": False,
        "profit_loss": 0,
        "price": 1566.8,
        "post_only": True,
        "order_type": "limit",
        "order_id": "ETH-32042537117",
        "mmp": False,
        "matching_id": None,
        "mark_price": 1566.77,
        "liquidity": "M",
        "label": "hedgingSpot-open-1677836948224",
        "instrument_name": "ETH-PERPETUAL",
        "index_price": 1566.95,
        "fee_currency": "ETH",
        "fee": 0,
        "direction": "sell",
        "api": True,
        "amount": 10
      }]


my_trades_path = system_tools.provide_path_for_file ('myTrades', 
                                                                            'eth',
                                                                            'open'
                                                                            )
pickling.replace_data (my_trades_path, 
                       my_trades_open, 
                       True
                       )


my_trades_path_open_recovery = system_tools.provide_path_for_file ('myTrades', 
                                                                    'eth',
                                                                    'open-recovery-point'
                                                                    )
pickling.replace_data (my_trades_path_open_recovery, 
                                                my_trades_open, 
                                                True
                                                )

net = number_modification.net_position (my_trades_open)
print (f' ALL {net}')

