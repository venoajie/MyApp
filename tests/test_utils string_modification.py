from src.utilities import string_modification

def test_remove_redundant_elements  ():
    element_numbers = ['BTC', 'BTC', 'BTC', 'ETH', 'ETH', 'LTC']
    element_strings = ['A', 'A', 'B', 'B', 'C', 'C']
    element_null = []

    data = [{'a': 1, 'b': 2}, {'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
    expected = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}]
    
    assert string_modification.remove_redundant_elements (data) == expected
    assert string_modification.remove_redundant_elements (element_numbers) == ['BTC','ETH','LTC']
    assert string_modification.remove_redundant_elements (element_strings) == ['A','B','C']
    assert string_modification.remove_redundant_elements (element_null) == []
    
def test_unique_elements  ():
    
    data1= [
        {
            'trade_seq': 5552, 'trade_id': 'ETH-16468267', 'timestamp': 1670380638979, 'tick_direction': 0, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
            'price': 1265.5, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256841', 'mmp': False, 
            'matching_id': None, 'mark_price': 1265.51, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-9DEC22', 
            'index_price': 1265.6, 'fee_currency': 'ETH', 'fee': -8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
        }, 
        
        {'trade_seq': 6613, 'trade_id': 'ETH-16468711', 'timestamp': 1670380845716, 'tick_direction': 0, 
         'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
         'price': 1265.25, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256847', 'mmp': False, 
         'matching_id': None, 'mark_price': 1265.25, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-16DEC22', 
         'index_price': 1265.84, 'fee_currency': 'ETH', 'fee':     -8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
         },
        
        {
            'trade_seq': 1814, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012391, 'tick_direction': 0, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
            'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705292', 'mmp': False, 
            'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671189554374', 'instrument_name': 'ETH-23DEC22', 
            'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
            },
        
        {
            'trade_seq': 1941, 'trade_id': 'ETH-16709956', 'timestamp': 1671200629432, 'tick_direction': 0, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
            'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106655076', 'mmp': False, 
            'matching_id': None, 'mark_price': 1212.25, 'liquidity': 'M', 'label': 'hedging spot-open-1671200377734', 'instrument_name': 'ETH-23DEC22', 
            'index_price': 1212.58, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
            }
        ]


    data2= [
        {
            'trade_seq': 5552, 'trade_id': 'ETH-16468267', 'timestamp': 1670380638979, 'tick_direction': 0, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
            'price': 1265.5, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256841', 'mmp': False, 
            'matching_id': None, 'mark_price': 1265.51, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-9DEC22', 
            'index_price': 1265.6, 'fee_currency': 'ETH', 'fee': -8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
        }, 
        
        {'trade_seq': 6613, 'trade_id': 'ETH-16468711', 'timestamp': 1670380845716, 'tick_direction': 0, 
         'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
         'price': 1265.25, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3058256847', 'mmp': False, 
         'matching_id': None, 'mark_price': 1265.25, 'liquidity': 'M', 'label': 'hedging spot', 'instrument_name': 'ETH-16DEC22', 
         'index_price': 1265.84, 'fee_currency': 'ETH', 'fee': -8.06e-06, 'direction': 'sell', 'api': True, 'amount': 102.0
         },
        
        {
            'trade_seq': 1814, 'trade_id': 'ETH-16709238', 'timestamp': 1671190012391, 'tick_direction': 0,
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
            'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3105705292', 'mmp': False, 
            'matching_id': None, 'mark_price': 1211.74, 'liquidity': 'M', 'label': 'hedging spot-open-1671189554374','instrument_name': 'ETH-23DEC22', 
            'index_price': 1211.95, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
            }
        ]
    

    result = [
        {
            'trade_seq': 1941, 'trade_id': 'ETH-16709956', 'timestamp': 1671200629432, 'tick_direction': 0, 
            'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 
            'price': 1211.9, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-3106655076', 'mmp': False,
            'matching_id': None, 'mark_price': 1212.25, 'liquidity': 'M', 'label': 'hedging spot-open-1671200377734', 'instrument_name': 'ETH-23DEC22', 
            'index_price': 1212.58, 'fee_currency': 'ETH', 'fee': -8.17e-06, 'direction': 'sell', 'api': True, 'amount': 99.0
            }
        ]
    
    data_A = [1, 2, 3, 4, 5]
    data_B = [2, 4]

    assert string_modification.find_unique_elements (data_A, data_B) == [1, 3, 5]  
    assert string_modification.find_unique_elements (data1, data2) == result      
    
def test_extract_currency_from_text  ():
    websocket_message_channel_user_portfolio_BTC = 'user.portfolio.BTC'
    websocket_message_channel_user_portfolio_ETH = 'user.portfolio.ETH'
    
    websocket_message_channel_user_trades_ETH = 'user.trades.future.ETH.100ms'
    websocket_message_channel_user_trades_BTC = 'user.trades.future.BTC.100ms'
    
    websocket_message_channel_user_orders_BTC = 'user.orders.future.BTC.raw'
    websocket_message_channel_user_orders_ETH = 'user.orders.future.ETH.raw'
    
    websocket_message_channel_book_BTC = 'book.BTC-29SEP23.none.20.100ms'
    websocket_message_channel_book_ETH = 'book.ETH-27JAN23.none.20.100m'
    
    websocket_message_channel_chart_BTC = 'chart.trades.BTC-PERPETUAL.1'
    websocket_message_channel_chart_ETH = 'chart.trades.ETH-PERPETUAL.1'
    
    websocket_message_channel_price_index_BTC = 'deribit_price_index.btc_usd'
    websocket_message_channel_price_index_ETH = 'deribit_price_index.eth_usd'
    
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_portfolio_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_portfolio_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_trades_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_trades_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_orders_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_orders_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_book_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_book_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_chart_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_chart_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_price_index_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_price_index_ETH) == 'eth'
    
def test_extract_integers_from_text  ():
    list_text = ['hedging spot-open-1671189554374', 'hedging spot-close-167118955437']
    list_int = [1671189554374, 167118955437]
    assert string_modification.extract_integers_from_text ('hedging spot-open-1671189554374') == 1671189554374    
    assert ([string_modification.extract_integers_from_text(o)  for o in list_text  ]) == [1671189554374, 167118955437]    
    assert string_modification.extract_integers_from_text ('hedging spot-open') == []    
    assert string_modification.extract_integers_from_text ('1671189554374') == 1671189554374
    
    