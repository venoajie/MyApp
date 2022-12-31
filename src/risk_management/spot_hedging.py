# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log

from utils import pickling, system_tools, string_modification
from portfolio.deribit import myTrades_management


@dataclass(unsafe_hash=True, slots=True)
class SpotHedging ():

    '''
    '''       
    label: str 
    my_trades: list = []
                
    def my_trades_api_basedOn_label (self) -> list:
        
        '''
        '''       
        my_trades = self.my_trades
        #log.error (my_trades)        

        #print (my_trades)
        #print ([o for o in my_trades  ])
        return   [] if my_trades  == [] else  ([o for o in my_trades if self.label in o['label']  ])


    def my_trades_api_basedOn_label_max_price_attributes (self) -> dict:
        
        '''
        '''       
        
        my_trades_api = self.my_trades_api_basedOn_label ()

        if my_trades_api_basedOn_label !=[]:
            max_price = max ([o['price'] for o in my_trades_api])
            trade_list_with_max_price =  ([o for o in my_trades_api if o['price'] == max_price ])
            len_trade_list_with_max_price = len(trade_list_with_max_price)
            
            # if multiple items, select only the oldest one
            if len_trade_list_with_max_price > 0:
                trade_list_with_max_price_min_timestamp = min([o['timestamp'] for o in trade_list_with_max_price])
                trade_list_with_max_price =  ([o for o in trade_list_with_max_price if o['timestamp'] == trade_list_with_max_price_min_timestamp ])
            
            return  {
                'max_price': max_price,
                'trade_id':  ([o['trade_id'] for o in trade_list_with_max_price])[0] ,
                'order_id':  ([o['order_id'] for o in trade_list_with_max_price])[0] ,
                'instrument':  ([o['instrument_name'] for o in trade_list_with_max_price])[0] ,
                'size':  ([o['amount'] for o in trade_list_with_max_price])[0] ,
                'label':  ([o['label'] for o in trade_list_with_max_price])[0] ,
            
            }
        if my_trades_api_basedOn_label ==[]:
            return []

    def my_trades_max_price_plus_threshold (self,
        threshold: float, 
        index_price: float, 
        ) -> float:
        
        '''
        '''       

        myTrades_max_price =  self.my_trades_api_basedOn_label_max_price_attributes () ['max_price']
        myTrades_max_price_plus_pct = myTrades_max_price * threshold
                                        
        return  {'index_price_higher_than_threshold': index_price > myTrades_max_price  + myTrades_max_price_plus_pct,
                'index_price_lower_than_threshold': index_price < myTrades_max_price - myTrades_max_price_plus_pct}

    def compute_minimum_hedging_size (self,
        notional: float,
        min_trade_amount: float,
        contract_size: int
        ) -> int:
        
        '''
        compute minimum hedging size

        '''       
        return  int ((notional / min_trade_amount * contract_size) + min_trade_amount)

    def compute_actual_hedging_size (self) -> int:
        
        '''
        compute actual hedging size

        '''       
        my_trades = self.my_trades_api_basedOn_label ()
        return  sum([o['amount'] for o in my_trades if self.label in o['label'] ])

    def compute_remain_unhedged (self,
        notional: float,
        min_trade_amount: float,
        contract_size: int
        ) -> int:

        '''
        '''       
        # compute minimum hedging size
        min_hedged_size: int = self.compute_minimum_hedging_size (notional, min_trade_amount, contract_size)
        
        # check whether current spot was hedged
        actual_hedging_size : int = self.compute_actual_hedging_size () 
        log.warning (f'{actual_hedging_size=}')

        # check remaining hedging needed
        return int(min_hedged_size if actual_hedging_size  == [] else min_hedged_size - actual_hedging_size )
        
    def is_spot_hedged_properly (self,
        notional: float,
        min_trade_amount: float,
        contract_size: int) -> dict:

        '''
        # check whether spot has hedged properly
        notional =  index_price * equity

        '''       
        # compute minimum hedging size
        min_hedged_size: int = self.compute_minimum_hedging_size (notional, min_trade_amount, contract_size)

        # check remaining hedging needed
        remain_unhedged: int = self.compute_remain_unhedged (
                                                        notional,
                                                        min_trade_amount,
                                                        contract_size
                                                        )
        # check open orders related to hedging, to ensure previous open orders has completely consumed
        
        size_pct_qty = int ((30/100 * min_hedged_size ))
        hedging_size_portion = int(size_pct_qty if remain_unhedged > size_pct_qty else remain_unhedged)

        none_data = [None, [], '0.0', 0]
            
        #log.critical (f'{open_orders_byAPI=}')        
        log.info (f'{min_hedged_size=}')        
        #log.info (f'{notional=}')        
        log.info (f'{remain_unhedged=} {remain_unhedged > 0=}')        
        log.info (f'{hedging_size_portion=}')  
        log.info (f'{remain_unhedged > 0=}')  
        return {'spot_was_unhedged': False if notional in none_data else remain_unhedged > 0,
                'all_hedging_size': min_hedged_size,
                'average_up': int(size_pct_qty),
                'hedging_size': hedging_size_portion}


    def summing_size_open_orders(self,
        open_orders_byAPI: list,
        ) -> int:
        
        '''
        # sum current open orders with 'hedging spot' label
        open_orders_byAPI =  open orders submitted by API/not manual (web = False)

        '''       
        return 0 if open_orders_byAPI == [] else sum ([o['amount']  for o in open_orders_byAPI if self.label in o['label'] ])


    def is_over_hedged (self,
        open_orders_byAPI: list,
        minimum_hedging_size: int) -> bool:

        '''
        # check open orders related to hedging, should be less than required hedging size. If potentially over-hedged, call cancel open orders function
        '''       
        return self.summing_size_open_orders (open_orders_byAPI) > minimum_hedging_size    
                
    def adjusting_inventories (self,
                               index_price: float,
                               threshold: float = .5/100,
                               label: str = 'hedging spot-open'
                               ) -> list:
        
        '''
        ''' 
        my_trades_mgt = myTrades_management.MyTrades (self.my_trades)

        my_trades_max_price_attributes_filteredBy_label = my_trades_mgt.my_trades_max_price_attributes_filteredBy_label (label)
        myTrades_max_price = my_trades_max_price_attributes_filteredBy_label ['max_price']
        
        myTrades_max_price_pct_x_threshold = myTrades_max_price * threshold
        myTrades_max_price_pct_minus = (myTrades_max_price - myTrades_max_price_pct_x_threshold)
        myTrades_max_price_pct_plus = (myTrades_max_price + myTrades_max_price_pct_x_threshold)
        

        myTrades_max_price_attributes_label = my_trades_max_price_attributes_filteredBy_label ['label']
        label_int = string_modification.extract_integers_from_text (myTrades_max_price_attributes_label)
        
        label_to_send = f'hedging spot-closed-{label_int}'
        
        log.debug(f'{myTrades_max_price_pct_minus=} {index_price=} {myTrades_max_price_pct_plus=} ')
        
        log.debug(f'trans.price {myTrades_max_price} take_profit {myTrades_max_price_pct_minus < index_price} average_up {myTrades_max_price_pct_plus > index_price} ')
        
        return {'take_profit': myTrades_max_price_pct_minus < index_price,
                'label_take_profit':  label_to_send,
                'size_take_profit':  my_trades_max_price_attributes_filteredBy_label ['size'],
                'average_up':  myTrades_max_price_pct_plus > index_price}
        
def my_path_myTrades (
    currency: str,
    status: str
    ) -> list:
    
    '''
    status = closed/open
    '''       
        
    return  system_tools.provide_path_for_file ('myTrades', currency, status)

def fetch_my_trades (
    currency: str,
    status: str
    ) -> list:
    
    '''
    '''       
    
    return  pickling.read_data (my_path_myTrades(currency, status)) 

def my_trades_api_basedOn_label (
    currency: str,
    status: str,
    label: str
    ) -> list:
    
    '''
    '''       
    my_trades = myTrades_management.MyTrades(fetch_my_trades (currency, status))    
    return  my_trades.my_trades_api_basedOn_label (label)
        
def separate_specific_label_trade (
    currency: str,
    status: str,
    label: str,
    closed_label: str,
    my_trades_api: list = None 
    )-> list:
    
    '''
    '''    
    if my_trades_api == None:
        my_trades_api = my_trades_api_basedOn_label (currency, status, label)

    return [] if my_trades_api == [] else  ([o for o in my_trades_api  if  closed_label in o['label'] ])

def separate_open_trades_pair_which_have_closed (
    currency: str,
    status: str,
    label: str,
    closed_label: str,
    my_trades_api: list = None  
    )-> list:
    
    '''
    looking for pair transaction attributes which have closed previously
    '''    
        
    from loguru import logger as log
    if my_trades_api == None:
        closed_trades = separate_specific_label_trade (currency, status,label, closed_label)
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
        pickling.append_data(my_path_myTrades(currency, 'closed'), closed_trades) 

