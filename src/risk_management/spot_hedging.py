# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log

from utilities import string_modification
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
        return   [] if my_trades  == [] else  ([o for o in my_trades if self.label in o['label']  ])

    def my_trades_api_basedOn_label_max_price_attributes (self) -> dict:
        
        '''
        '''       
        
        my_trades_api = self.my_trades_api_basedOn_label ()

        if my_trades_api !=[]:
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
                'label':  ([o['label'] for o in trade_list_with_max_price])[0]
                }
            
        if my_trades_api ==[]:
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
        return  -(int ((notional / min_trade_amount * contract_size) + min_trade_amount))

    def net_position (self, 
                      selected_transactions: list
                      )-> float:
        
        '''
        '''    
        from utilities import number_modification                
        return number_modification.net_position (selected_transactions)
    
    def compute_actual_hedging_size (self) -> int:
        
        '''
        compute actual hedging size

        '''  
        my_trades = self.my_trades_api_basedOn_label ()
        #log.error (my_trades)
        
        if     my_trades != [] :
            my_trades_label = ([o for o in my_trades if self.label in o['label'] ])
            #log.error (my_trades_label)
        return 0 if my_trades == [] else self.net_position (my_trades_label)

    def compute_remain_unhedged (self,
        notional: float,
        min_trade_amount: float,
        contract_size: int
        ) -> int:

        '''
        '''       
        # compute minimum hedging size. negative sign since the direction is expected as 'sell
        min_hedged_size: int = (self.compute_minimum_hedging_size (notional, min_trade_amount, contract_size))
        
        # check whether current spot was hedged
        actual_hedging_size : int = self.compute_actual_hedging_size () 
        log.warning (f'{actual_hedging_size=}')

        # check remaining hedging needed
        return int(min_hedged_size if actual_hedging_size  == [] else min_hedged_size - actual_hedging_size )
        
    def is_spot_hedged_properly (self,
        notional: float,
        min_trade_amount: float,
        contract_size: int
        ) -> dict:

        '''
        # check whether spot has hedged properly
        notional =  index_price * equity

        '''       
        # compute minimum hedging size
        min_hedged_size: int = self.compute_minimum_hedging_size (notional, 
                                                                  min_trade_amount, 
                                                                  contract_size)

        # check remaining hedging needed
        remain_unhedged: int = self.compute_remain_unhedged (
                                                        notional,
                                                        min_trade_amount,
                                                        contract_size
                                                        )
        # check open orders related to hedging, to ensure previous open orders has completely consumed
        
        size_pct_qty = int ((30/100 * min_hedged_size ))
        hedging_size_portion = int(size_pct_qty if remain_unhedged < size_pct_qty else remain_unhedged)

        none_data = [None, [], '0.0', 0]
            
        #log.critical (f'{open_orders_byAPI=}')        
        log.info (f'{min_hedged_size=}')        
        #log.info (f'{notional=}')        
        log.info (f'{remain_unhedged=} {remain_unhedged > 0=}')        
        log.info (f'{hedging_size_portion=}')  
        log.info (f'{remain_unhedged < 0=}')  
        return {'spot_was_unhedged': False if notional in none_data else remain_unhedged < 0,
                'all_hedging_size': min_hedged_size,
                'average_up_size': max(1,int(size_pct_qty/3)),
                'hedging_size': hedging_size_portion}

    def adjusting_inventories (self,
                               index_price: float,
                               currency: str,
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

        trades_to_close = ([o for o in (self.my_trades) if  str(label_int)  in o['label'] ])
        # sum transaction with the same label id
        log.debug(f'{trades_to_close=} ')
        #log.debug(f'{str(label_int) =} ')
        size_take_profit = my_trades_max_price_attributes_filteredBy_label ['size']
        #log.debug(f'{size_take_profit=} ')
        sum_closed_trades_in_my_trades_open_net = my_trades_mgt.my_trades_api_net_position (trades_to_close)
        avoid_over_bought = sum_closed_trades_in_my_trades_open_net + size_take_profit == 0
        
        if avoid_over_bought == False:        
            my_trades = myTrades_management.MyTrades (trades_to_close)
            my_trades.distribute_trade_transaction(currency)
        
        label_to_send = f'hedging spot-closed-{label_int}'
        
        log.debug(f'trans.price {myTrades_max_price}   {index_price=}  {avoid_over_bought=} ')
        log.debug(f'take_profit {index_price <  myTrades_max_price_pct_minus} average_up {index_price  > myTrades_max_price_pct_plus} ')
        log.debug(f'{myTrades_max_price_pct_minus=}  {myTrades_max_price_pct_plus=} {sum_closed_trades_in_my_trades_open_net=} ')
        
        
        return {'take_profit':  index_price <  myTrades_max_price_pct_minus and avoid_over_bought,
                'buy_price':  myTrades_max_price_pct_minus,
                'sell_price':  myTrades_max_price_pct_plus,
                'label_take_profit':  label_to_send,
                'size_take_profit':  size_take_profit,
                'average_up':  index_price  > myTrades_max_price_pct_plus}#
        