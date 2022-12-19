# -*- coding: utf-8 -*-
from utils import pickling, system_tools  
from portfolio.deribit import myTrades_management

def fetch_my_trades (
    currency: str
    ) -> list:
    
    '''
    '''       
    
    file_name_myTrades = (f'{currency.lower()}-myTrades-open.pkl')
    
    my_path_myTrades = system_tools.provide_path_for_file (file_name_myTrades, "portfolio", "deribit")
    
    return  pickling.read_data (my_path_myTrades) 

def my_trades_api_basedOn_label (
    currency: str,
    label: str
    ) -> list:
    
    '''
    '''       
    

    #print (label)
    my_trades = myTrades_management.MyTrades(fetch_my_trades (currency))    
    return  my_trades.my_trades_api_basedOn_label (label)

def my_trades_api_basedOn_label_max_price_attributes (
    currency: str,
    label: str
    ) -> float:
    
    '''
    '''       
       
    my_trades_api = my_trades_api_basedOn_label (currency, label)
    #print (my_trades_api_basedOn_label)
    if my_trades_api_basedOn_label !=[]:
        max_price = max ([o['price'] for o in my_trades_api])
        trade_list_with_max_price =  ([o for o in my_trades_api if o['price'] == max_price ])
        len_trade_list_with_max_price = len(trade_list_with_max_price)
        
        # if multiple items, select only the oldest one
        if len_trade_list_with_max_price > 0:
            trade_list_with_max_price_min_timestamp = min([o['timestamp'] for o in trade_list_with_max_price])
            trade_list_with_max_price =  ([o for o in trade_list_with_max_price if o['timestamp'] == trade_list_with_max_price_min_timestamp ])
        
        return  {
            'price': max_price,
            'trade_id':  ([o['trade_id'] for o in trade_list_with_max_price])[0] ,
            'order_id':  ([o['order_id'] for o in trade_list_with_max_price])[0] ,
            'size':  ([o['amount'] for o in trade_list_with_max_price])[0] ,
            'label':  ([o['label'] for o in trade_list_with_max_price])[0] ,
        
        }
    if my_trades_api_basedOn_label ==[]:
        return []

def my_trades_max_price_plus_threshold (currency: str,
    threshold: float, 
    index_price: float, 
    label: str
    ) -> float:
    
    '''
    '''       

    myTrades_max_price =  my_trades_api_basedOn_label_max_price_attributes (currency, label) ['price']
    myTrades_max_price_plus_pct = myTrades_max_price * threshold
                                    
    return  {'index_price_higher_than_threshold': index_price > myTrades_max_price  + myTrades_max_price_plus_pct,
             'index_price_lower_than_threshold': index_price < myTrades_max_price - myTrades_max_price_plus_pct}

def summing_size_open_orders_basedOn_label(
    open_orders_byBot: list,
    label: str 
    ) -> int:
    
    '''
    # sum current open orders with 'hedging spot' label
    open_orders_byBot =  open orders submitted by API/not manual (web = False)

    '''       

    none_data = [None, [], '0.0', 0]
    try:
        open_orders_hedging = open_orders_byBot
    except:
        open_orders_hedging = open_orders_byBot ['result']

    return 0 if open_orders_hedging in none_data else sum ([o['amount']  for o in open_orders_hedging if label in o['label'] ])


def compute_minimum_hedging_size (
    notional: float,
    min_trade_amount: float,
    contract_size: int
    ) -> int:
    
    '''
    compute minimum hedging size

    '''       
    return  int ((notional / min_trade_amount * contract_size) + min_trade_amount)


def compute_actual_hedging_size (
    currency: str,
    label: str,
    ) -> int:
    
    '''
    compute actual hedging size

    '''       
    my_trades = my_trades_api_basedOn_label (currency,
                                             label
                                             )
    return  sum([o['amount'] for o in my_trades if label in o['label'] ])

def is_spot_hedged_properly (
    hedging_instruments: list,
    position: list,
    open_orders_byBot: list,
    notional: float,
    min_trade_amount: float,
    contract_size: int) -> dict:

    '''
    # check whether spot has hedged properly
    notional =  index_price * equity

    '''       
    # compute minimum hedging size
    min_hedged_size: int = compute_minimum_hedging_size (notional, min_trade_amount, contract_size)
    
    # check whether current spot was hedged
    actual_hedging_size : int = compute_actual_hedging_size (hedging_instruments, position) #! how to distinguish multiple strategy? (need to check label)

    # check remaining hedging needed
    remain_unhedged: int = int(min_hedged_size if actual_hedging_size  == [] else min_hedged_size + actual_hedging_size )

    # check open orders related to hedging, to ensure previous open orders has completely consumed
    open_orders_hedging_size = summing_size_open_orders_basedOn_label (open_orders_byBot, 'hedging spot-open')
    
    size_pct_qty = int ((10/100 * min_hedged_size ))
    hedging_size_portion = int(size_pct_qty if remain_unhedged > size_pct_qty else remain_unhedged)

    none_data = [None, [], '0.0', 0]
        
    return {'spot_was_unhedged': False if notional in none_data else open_orders_hedging_size in none_data and remain_unhedged > 0,
            'hedging_size': hedging_size_portion}

def is_over_hedged (
    open_orders_byBot: list,
    minimum_hedging_size: int,
    label) -> bool:

    '''
    # check open orders related to hedging, should be less than required hedging size. If potentially over-hedged, call cancel open orders function
    '''       
    return summing_size_open_orders_basedOn_label (open_orders_byBot, label) > minimum_hedging_size    
        