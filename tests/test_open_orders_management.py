# -*- coding: utf-8 -*-

from src.transaction_management.deribit import open_orders_management
#from portfolio.deribit import open_orders_management

my_orders_all = [
    {
        'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097385800', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671093368895, 'label': 'hedgingSpot-open-1671093365868', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093368895, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
        }, 
    {
        'web': True, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1300.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097383152', 'mmp': False, 'max_show': 5.0, 'last_update_timestamp': 1671093338010, 'label': '', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093338010, 'commission': 0.0, 'average_price': 0.0, 'api': False, 'amount': 5.0
        },
    {
        'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097524136', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671095068918, 'label': 'hedgingSpot-open-1671095066375', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671095068918, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
        }
    ]
    
my_orders_with_api_true = [
    {
        'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097385800', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671093368895, 'label': 'hedgingSpot-open-1671093365868', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093368895, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
        }, 
    {
        'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097524136', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671095068918, 'label': 'hedgingSpot-open-1671095066375', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671095068918, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
        }
     
    ]

my_orders_with_manual = [
    {
        'web': True, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1300.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097383152', 'mmp': False, 'max_show': 5.0, 'last_update_timestamp': 1671093338010, 'label': '', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093338010, 'commission': 0.0, 'average_price': 0.0, 'api': False, 'amount': 5.0
     }
    ]

my_orders_none = []


open_orders = open_orders_management.MyOrders (my_orders_all)
open_orders_blank = open_orders_management.MyOrders (my_orders_none)
    
def test_my_orders_api  ():
    assert open_orders.open_orders_api () == my_orders_with_api_true
    assert open_orders_blank.open_orders_api () == []
    
def test_my_orders_manual  ():
    
    assert open_orders.open_orders_manual () == my_orders_with_manual
    assert open_orders_blank.open_orders_manual () == []
    
def test_my_orders_api_basedOn_label ():
    
    assert open_orders.open_orders_api_basedOn_label ("hedgingSpot") == my_orders_with_api_true
    assert open_orders_blank.open_orders_api_basedOn_label ("hedgingSpot") == []
    
def test_my_orders_api_last_update_timestamp  ():
    assert open_orders.open_orders_api_last_update_timestamps () == [1671093368895, 1671095068918]
    assert open_orders_blank.open_orders_api_last_update_timestamps () == []
    
def test_my_orders_api_basedOn_label_items_qty  ():
    assert open_orders.open_orders_api_basedOn_label_items_qty ("hedgingSpot") == 2

def test_combine_open_orders_based_on_id ():

    open_orders_open = [{'order_id': 1}, {'order_id': 2}, {'order_id': 3}]
    order_id = 2
    expected_result = {'item_with_same_id': [{'order_id': 2}],
                           'item_with_diff_id': [{'order_id': 1}, {'order_id': 3}]
                           }
    assert open_orders.combine_open_orders_based_on_id (open_orders_open, 
                                                        order_id
                                                        ) == expected_result
    
def test_recognize_order_transactions ():

        order_open =  {
        'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097385800', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671093368895, 'label': 'hedgingSpot-open-1671093365868', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093368895, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
        }
        
        expected_result = {'order_state_open': True, 'order_state_else': False, 'order_id': 'ETH-3097385800'}
        assert open_orders.recognize_order_transactions(order_open) == expected_result

def test_recognize_order_transactions ():

    my_orders_get= [
        {
            'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097385800', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671093368895, 'label': 'hedgingSpot-open-1671093365868', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093368895, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
            }, 
        {
            'web': True, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1300.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097383152', 'mmp': False, 'max_show': 5.0, 'last_update_timestamp': 1671093338010, 'label': '', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093338010, 'commission': 0.0, 'average_price': 0.0, 'api': False, 'amount': 5.0
            },
        {
            'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097524136', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671095068918, 'label': 'hedgingSpot-open-1671095066375', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671095068918, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
            }
        ]
    assert open_orders.compare_open_order_per_db_vs_get(my_orders_get) == True

    my_orders_get= [
        {
            'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'closed', 'order_id': 'ETH-3097385800', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671093368895, 'label': 'hedgingSpot-open-1671093365868', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093368895, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
            }, 
        {
            'web': True, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1300.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097383152', 'mmp': False, 'max_show': 5.0, 'last_update_timestamp': 1671093338010, 'label': '', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671093338010, 'commission': 0.0, 'average_price': 0.0, 'api': False, 'amount': 5.0
            },
        {
            'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': True, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1323.05, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-3097524136', 'mmp': False, 'max_show': 108.0, 'last_update_timestamp': 1671095068918, 'label': 'hedgingSpot-open-1671095066375', 'is_liquidation': False, 'instrument_name': 'ETH-23DEC22', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1671095068918, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 108.0
            }
        ]
    assert open_orders.compare_open_order_per_db_vs_get(my_orders_get) == False


def test_open_orderLabelCLosed ():

    my_orders_get= [
        {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': True, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1475.5, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31958754973', 'mmp': False, 'max_show': 24.0, 'last_update_timestamp': 1677500787119, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677474762554, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 24.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1675.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31958514019', 'mmp': False, 'max_show': 8.0, 'last_update_timestamp': 1677473096657, 'label': 'supplyDemandShort60-open-1677473096745', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'sell', 'creation_timestamp': 1677473096657, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 8.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1490.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941729757', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361995418, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361995418, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1550.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941709815', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361867909, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361867909, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1535.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941707258', 'mmp': False, 'max_show': 10.0, 'last_update_timestamp': 1677361847107, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361847107, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 10.0}, {'web': False, 'time_in_force': 'good_til_cancelled', 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1512.0, 'post_only': True, 'order_type': 'limit', 'order_state': 'open', 'order_id': 'ETH-31941700022', 'mmp': False, 'max_show': 14.0, 'last_update_timestamp': 1677361811798, 'label': 'test-closed-1677059533', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'filled_amount': 0.0, 'direction': 'buy', 'creation_timestamp': 1677361811798, 'commission': 0.0, 'average_price': 0.0, 'api': True, 'amount': 14.0}, {'web': False, 'triggered': False, 'trigger_price': 1570.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1570.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTS-5652932', 'mmp': False, 'max_show': 9.0, 'last_update_timestamp': 1677473096934, 'label': 'supplyDemandLong60-closed-1677473096934', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677473096934, 'api': True, 'amount': 9.0}, {'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5652931', 'mmp': False, 'max_show': 8.0, 'last_update_timestamp': 1677473096745, 'label': 'supplyDemandShort60-closed-1677473096745', 'is_liquidation': False, 'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677473096745, 'api': True, 'amount': 8.0}
        ]
    
    assert open_orders.open_orderLabelCLosed(my_orders_get) ==  [1677059533, 601677473096934]
    
    
def test_is_open_trade_has_exit_order ():
    from src.strategies import entries_exits
    from src.utilities import string_modification
    
    open_trade =  [
        {'trade_seq': 118020115, 'trade_id': 'ETH-160804604', 'timestamp': 1677059533908, 'tick_direction': 1, 'state': 'filled', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1640.85, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31873685113', 'mmp': False, 'matching_id': None, 'mark_price': 1640.88, 'liquidity': 'M', 
         'label': 'test-open-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1641.03, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 78.0
         }, 
        {'trade_seq': 118647438, 'trade_id': 'ETH-161557067', 'timestamp': 1677807144369, 'tick_direction': 2, 'state': 'filled',
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.00039974, 'price': 1535, 'post_only': True,
         'order_type': 'limit', 'order_id': 'ETH-31941707258', 'mmp': False, 'matching_id': None, 'mark_price': 1544.41, 'liquidity': 'M',
         'label': 'test-closed-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1552.18, 'fee_currency': 'ETH', 'fee': 0,
         'direction': 'buy', 'api': True, 'amount': 10
         }, 
        {'trade_seq': 118697746, 'trade_id': 'ETH-161622575', 'timestamp': 1677835222867, 'tick_direction': 1, 'state': 'filled',
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0, 'price': 1569.65, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-32042276354', 'mmp': False, 'matching_id': None, 'mark_price': 1569.81, 'liquidity': 'M', 
         'label': 'hedgingSpot-open-1677835222468', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1570.19, 'fee_currency': 'ETH', 'fee': 0, 
         'direction': 'sell', 'api': True, 'amount': 7}, 
        {'trade_seq': 118646176, 'trade_id': 'ETH-161555549', 'timestamp': 1677807136264, 'tick_direction': 3, 'state': 'filled', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0003367, 'price': 1550, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31941709815', 'mmp': False, 'matching_id': None, 'mark_price': 1555.56, 'liquidity': 'M', 
         'label': 'test-closed-1677059533', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1560.48, 'fee_currency': 'ETH', 'fee': 0,
         'direction': 'buy', 'api': True, 'amount': 10
         },
        {'trade_seq': 115425899, 'trade_id': 'ETH-157512749', 'timestamp': 1674106201607, 'tick_direction': 3, 'state': 'filled', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.05, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31266368853', 'mmp': False, 'matching_id': None, 'mark_price': 1528.33, 'liquidity': 'M', 
         'label': 'hedgingSpot-open-1674106085', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.78, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 7.0
         },
        {'trade_seq': 115426103, 'trade_id': 'ETH-157513016', 'timestamp': 1674106959423, 'tick_direction': 0, 'state': 'filled',
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1527.2, 'post_only': True,
         'order_type': 'limit', 'order_id': 'ETH-31266435353', 'mmp': False, 'matching_id': None, 'mark_price': 1526.81, 'liquidity': 'M', 
         'label': 'hedgingSpot-open-1674106880', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1526.99, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 7.0
         }, 
        {'trade_seq': 115426211, 'trade_id': 'ETH-157513139', 'timestamp': 1674107594720, 'tick_direction': 1, 'state': 'open', 
         'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 
         'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.62, 'liquidity': 'M',
         'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.52, 'fee_currency': 'ETH', 'fee': 0.0, 
         'direction': 'sell', 'api': True, 'amount': 11.0
         }, {'trade_seq': 115426212, 'trade_id': 'ETH-157513141', 'timestamp': 1674107600323, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1528.4, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31266497562', 'mmp': False, 'matching_id': None, 'mark_price': 1528.61, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674107582', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1528.55, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 45.0}, {'trade_seq': 115440589, 'trade_id': 'ETH-157532557', 'timestamp': 1674134437352, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1514.1, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269839438', 'mmp': False, 'matching_id': None, 'mark_price': 1514.49, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134423', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1514.57, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 4.0}, {'trade_seq': 115441415, 'trade_id': 'ETH-157533765', 'timestamp': 1674134974683, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1524.95, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31269979727', 'mmp': False, 'matching_id': None, 'mark_price': 1525.19, 'liquidity': 'M', 'label': 'hedgingSpot-open-1674134971', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1524.87, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'sell', 'api': True, 'amount': 1.0}, {'trade_seq': 118355869, 'trade_id': 'ETH-161212758', 'timestamp': 1677474758759, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': -0.00011743, 'price': 1635.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31958514035', 'mmp': False, 'matching_id': None, 'mark_price': 1635.17, 'liquidity': 'M', 'label': 'supplyDemandLong60-open-1677473096934', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1635.36, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 9.0}, {'trade_seq': 118554841, 'trade_id': 'ETH-161447719', 'timestamp': 1677716308851, 'tick_direction': 1, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0, 'price': 1675, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-31958514019', 'mmp': False, 'matching_id': None, 'mark_price': 1675.06, 'liquidity': 'M', 'label': 'supplyDemandShort60-open-1677473096', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1674.09, 'fee_currency': 'ETH', 'fee': 0, 'direction': 'sell', 'api': True, 'amount': 8}, {'trade_seq': 118698584, 'trade_id': 'ETH-161624004', 'timestamp': 1677836968025, 'tick_direction': 3, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 0, 'price': 1566.8, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32042537117', 'mmp': False, 'matching_id': None, 'mark_price': 1566.77, 'liquidity': 'M', 'label': 'hedgingSpot-open-1677836948224', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1566.95, 'fee_currency': 'ETH', 'fee': 0, 'direction': 'sell', 'api': True, 'amount': 10}, {'trade_seq': 118754111, 'trade_id': 'ETH-161694237', 'timestamp': 1677962858339, 'tick_direction': 2, 'state': 'filled', 'self_trade': False, 'risk_reducing': False, 'reduce_only': False, 'profit_loss': 3.886e-05, 'price': 1550.0, 'post_only': True, 'order_type': 'limit', 'order_id': 'ETH-32055316625', 'mmp': False, 'matching_id': None, 'mark_price': 1550.34, 'liquidity': 'M', 'label': 'supplyDemandLong60B-open-1677903684425', 'instrument_name': 'ETH-PERPETUAL', 'index_price': 1550.76, 'fee_currency': 'ETH', 'fee': 0.0, 'direction': 'buy', 'api': True, 'amount': 5.0}
        ]

    open_orders = [
        {
            'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5655271', 'mmp': False, 'max_show': 9.0,
            'last_update_timestamp': 1677934800237, 'label': 'supplyDemandShort60-closed-1677934800137', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677934800237, 'api': True, 'amount': 9.0
            }, 
        {
            'web': False, 'triggered': False, 'trigger_price': 1600.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled',
            'stop_price': 1600.0, 'risk_reducing': False, 'replaced': False, 'reject_post_only': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 1610.0, 
            'post_only': True, 'order_type': 'take_limit', 'order_state': 'untriggered', 'order_id': 'ETH-TPTS-5655237', 'mmp': False, 'max_show': 5.0,
            'last_update_timestamp': 1677903684561, 'label': 'supplyDemandLong60B-closed-1677903684425', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677903684561, 'api': True, 'amount': 5.0
            },
        {
            'web': False, 'triggered': False, 'trigger_price': 1420.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1420.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTS-5655236', 'mmp': False, 'max_show': 5.0, 
            'last_update_timestamp': 1677903684513, 'label': 'supplyDemandLong60B-closed-1677903684425', 'is_liquidation': False, 
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'sell', 'creation_timestamp': 1677903684513, 'api': True, 'amount': 5.0
            }, 
        {
            'web': False, 'triggered': False, 'trigger_price': 1720.0, 'trigger': 'last_price', 'time_in_force': 'good_til_cancelled', 
            'stop_price': 1720.0, 'risk_reducing': False, 'replaced': False, 'reduce_only': False, 'profit_loss': 0.0, 'price': 'market_price', 
            'post_only': False, 'order_type': 'stop_market', 'order_state': 'untriggered', 'order_id': 'ETH-SLTB-5652931', 'mmp': False, 'max_show': 8.0, 
            'last_update_timestamp': 1677473096745, 'label': 'supplyDemandShort60-closed-1677473096', 'is_liquidation': False,
            'instrument_name': 'ETH-PERPETUAL', 'direction': 'buy', 'creation_timestamp': 1677473096745, 'api': True, 'amount': 8.0
            }
        ]
    
    open_orders = open_orders_management.MyOrders (open_orders)
    exclude = ['test', 'hedgingSpot']
    strategies =  string_modification.remove_redundant_elements([ string_modification.get_strings_before_character(o['label'])  for o in open_trade ]) 
    
    for strategy in strategies: 
        #print (strategy)
        if strategy == 'supplyDemandShort60-1677473096':
            assert open_orders.net_sum_trade_size_based_on_label_strategy(open_trade, strategy) ==  -8
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['is_sl_ok']==  True
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['size_sl']==  0
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['label_sl']==  'supplyDemandShort60-closed-1677473096'
            
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['is_tp_ok']==  False
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['size_tp']==  8
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['label_tp']==  'supplyDemandShort60-closed-1677473096'
            
        if strategy == 'supplyDemandLong60-1677473096934':
            assert open_orders.net_sum_trade_size_based_on_label_strategy(open_trade, strategy) ==  9
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['is_sl_ok']==  False
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['size_sl']==  9
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['label_sl']==  'supplyDemandLong60-closed-1677473096934'
            
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['is_tp_ok']==  False
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['size_tp']==  9
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['label_tp']==  'supplyDemandLong60-closed-1677473096934'
            
        if strategy == 'supplyDemandLong60B-1677903684425':
            assert open_orders.net_sum_trade_size_based_on_label_strategy(open_trade, strategy) ==  5
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['is_sl_ok']==  True
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['size_sl']==  0
            assert open_orders.is_open_trade_has_exit_order_sl(open_trade,strategy) ['label_sl']==  'supplyDemandLong60B-closed-1677903684425'
            
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['is_tp_ok']==  True
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['size_tp']==  0
            assert open_orders.is_open_trade_has_exit_order_tp(open_trade,strategy) ['label_tp']==  'supplyDemandLong60B-closed-1677903684425'
    