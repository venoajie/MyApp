# -*- coding: utf-8 -*-
from utils import pickling, system_tools, string_modification
from portfolio.deribit import myTrades_management

def my_path_myTrades (
    currency: str,
    status: str
    ) -> list:
    
    '''
    status = closed/open
    '''       
    
    file_name_myTrades = (f'{currency.lower()}-myTrades-{status}.pkl')
    
    return  system_tools.provide_path_for_file (file_name_myTrades, "portfolio", "deribit")

def fetch_my_trades (
    currency: str
    ) -> list:
    
    '''
    '''       
    
    #file_name_myTrades = (f'{currency.lower()}-myTrades-open.pkl')
    
    #my_path_myTrades = system_tools.provide_path_for_file (file_name_myTrades, "portfolio", "deribit")
    #print_path = pickling.read_data (my_path_myTrades(currency, 'open')) 
    #print (print_path)
    
    return  pickling.read_data (my_path_myTrades(currency, 'open')) 

def my_trades_api_basedOn_label (
    currency: str,
    label: str
    ) -> list:
    
    '''
    '''       
    my_trades = myTrades_management.MyTrades(fetch_my_trades (currency))    
    return  my_trades.my_trades_api_basedOn_label (label)

def separate_specific_label_trade (
    currency: str,
    label: str,
    closed_label: str,
    my_trades_api: list = None 
    )-> list:
    
    '''
    '''    
    if my_trades_api == None:
        my_trades_api = my_trades_api_basedOn_label (currency, label)

    return [] if my_trades_api == [] else  ([o for o in my_trades_api  if  closed_label in o['label'] ])

def separate_open_trades_pair_which_have_closed (
    currency: str,
    label: str,
    closed_label: str,
    my_trades_api: list = None  
    )-> list:
    
    '''
    looking for pair transaction attributes which have closed previously
    '''    
        
    from loguru import logger as log
    if my_trades_api == None:
        closed_trades = separate_specific_label_trade (currency, label, closed_label)
        my_trades_api = my_trades_api_basedOn_label (currency, label)
    else:
        closed_trades = separate_specific_label_trade (currency, label, closed_label, my_trades_api)
        
    closed_trades_label =  ([o['label'] for o in closed_trades ])
    closed_trades_label_int = ([string_modification.extract_integers_from_text(o)  for o in closed_trades_label  ])

    if len (closed_trades_label_int) !=[]:
        closed_trades_label_int = closed_trades_label_int[0] 
    else:
        return []
        
    return {'closed_trades': [] if closed_trades == [] else  ([o for o in my_trades_api if  str(closed_trades_label_int)  in o['label'] ]),
            'remaining_open_trades': [] if my_trades_api == [] else  ([o for o in my_trades_api if  str(closed_trades_label_int)  not in o['label'] ])
                }

def transfer_open_trades_pair_which_have_closed_to_closedTradingDb (
    currency: str,
    label: str,
    closed_label: str,
    my_trades_api: list = None  
    )-> list:
    
    '''
    looking for pair transaction attributes which have closed previously
    '''    
        
    if my_trades_api == None:
        open_trades = separate_open_trades_pair_which_have_closed (currency,
                                                                     label,
                                                                     closed_label
                                                                     )['remaining_open_trades']
        closed_trades = separate_open_trades_pair_which_have_closed (currency,
                                                                     label,
                                                                     closed_label
                                                                     )['closed_trades']
    else:
        open_trades = separate_open_trades_pair_which_have_closed (currency,
                                                                     label,
                                                                     closed_label, 
                                                                     my_trades_api
                                                                     )['remaining_open_trades']
        closed_trades = separate_open_trades_pair_which_have_closed (currency,
                                                                     label,
                                                                     closed_label, 
                                                                     my_trades_api
                                                                     )['closed_trades']
    if closed_trades != []  :
        from utils import pickling

        # write new data to remaining open transactions
        pickling.replace_data(my_path_myTrades(currency, 'open'), open_trades) 

        # append new data to closed transactions
        pickling.append_data(my_path_myTrades(currency, 'close'), closed_trades) 

def my_trades_api_basedOn_label_max_price_attributes (
    currency: str,
    label: str
    ) -> dict:
    
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

def my_trades_max_price_plus_threshold (
    currency: str,
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
    print (my_trades)
    return  sum([o['amount'] for o in my_trades if label in o['label'] ])

def is_spot_hedged_properly (
    currency: list,
    label: list,
    open_orders_byBot: list,
    notional: float,
    min_trade_amount: float,
    contract_size: int) -> dict:

    '''
    # check whether spot has hedged properly
    notional =  index_price * equity

    '''       
    from loguru import logger as log
    # compute minimum hedging size
    min_hedged_size: int = compute_minimum_hedging_size (notional, min_trade_amount, contract_size)
    log.warning (f'{min_hedged_size=}')
    
    # check whether current spot was hedged
    actual_hedging_size : int = compute_actual_hedging_size (currency, label) 
    log.error (f'{actual_hedging_size=}')

    # check remaining hedging needed
    remain_unhedged: int = int(min_hedged_size if actual_hedging_size  == [] else min_hedged_size - actual_hedging_size )
    log.error (f'{remain_unhedged=}')

    # check open orders related to hedging, to ensure previous open orders has completely consumed
    open_orders_hedging_size = summing_size_open_orders_basedOn_label (open_orders_byBot, 'hedging spot-open')
    log.warning (f'{open_orders_hedging_size=}')
    
    size_pct_qty = int ((10/100 * min_hedged_size ))
    hedging_size_portion = int(size_pct_qty if remain_unhedged > size_pct_qty else remain_unhedged)

    none_data = [None, [], '0.0', 0]
    log.critical (f'{notional=}')
        
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
        
    