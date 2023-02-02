# -*- coding: utf-8 -*-

from src.portfolio.deribit import open_orders_management
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
