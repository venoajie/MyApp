# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from strategies import hedging_spot
from risk_management import position_sizing
from db_management import sqlite_management
#from strategies import basic_strategy
from strategies.basic_strategy import BasicStrategy 


@dataclass(unsafe_hash=True, slots=True)
class MarketMaker(BasicStrategy):

    """ """

    def get_basic_params(self) -> dict:
        """
        """
        return BasicStrategy(self.strategy_label)

    async def is_send_open_order_allowed (self,
                                          notional: float,
                                          ask_price: float,
                                          bid_price: float
                                          ) -> dict:
        """

        Args:

        Returns:
            dict

        """
        strategy_config= self.get_basic_params().get_strategy_config()
        orders= await self.get_basic_params().get_orders_attributes()
        len_orders= orders['transactions_len']
        my_trades= await elf.get_basic_params().get_my_trades_attributes()
        len_my_trades= my_trades['transactions_len']

        order_allowed= True
        
        
        if order_allowed:
            
            # get transaction parameters        
            params= self.get_basic_params().get_basic_opening_paramaters(notional)
            
            # get transaction label and update the respective parameters
            label_main= strategy_config['strategy']
            label_open = hedging_spot.get_label ('open', label_main) 
            params.update({"label": label_open})
            
            params.update({"side": strategy_config['side']})
            if params['side']=='sell':
                params.update({"entry_price": ask_price})
            if params['side']=='buy':
                params.update({"entry_price": bid_price})
        
        return dict(order_allowed= order_allowed,
                    order_parameters= [] if order_allowed== False else params)
        
    def is_send_exit_order_allowed (ask_price: float,
                                    bid_price: float,
                                    current_outstanding_order_len: int,
                                    selected_transaction: list,
                                    strategy_attributes_for_hedging: list,
                                    ) -> dict:
        """

        Args:

        Returns:
            dict

        """
        # transform to dict
        transaction= selected_transaction[0]
        
        # get price
        last_transaction_price= transaction['price']
        
        transaction_side= transaction['direction']

        # get take profit pct
        tp_pct= strategy_attributes_for_hedging["take_profit_pct"]

        # get transaction parameters
        params= hedging_spot.get_basic_closing_paramaters(selected_transaction)
        
        if transaction_side=='sell':
            tp_price_reached= hedging_spot.is_transaction_price_minus_below_threshold(last_transaction_price,
                                                                        bid_price,
                                                                        tp_pct
                                                                        )
            params.update({"entry_price": bid_price})
            
        if transaction_side=='buy':
            tp_price_reached= hedging_spot.is_transaction_price_plus_above_threshold(last_transaction_price,
                                                                        ask_price,
                                                                        tp_pct
                                                                        )
            params.update({"entry_price": ask_price})
            params['side']='sell'
        
        print(f'tp_price_reached {tp_price_reached}')
        no_outstanding_order= current_outstanding_order_len < 1

        order_allowed= tp_price_reached\
                and no_outstanding_order 
        
        if order_allowed:
            
            params.update({"instrument":  transaction['instrument_name']})
            
        return dict(order_allowed= order_allowed,
                    order_parameters= [] if order_allowed== False else params)
        
    def size_adjustment (len_transaction: int, max_factor)-> float:
        """

        Args:

        Returns:
            bool

        """

        if len_transaction== 0:
            adjusting_factor= 1
        
        elif len_transaction== 1:
            adjusting_factor= 2/max_factor
                
        elif len_transaction== 2:
            adjusting_factor= 1/max_factor
        
        else:
            adjusting_factor= 0
        
        return adjusting_factor
        
    def delta_time (server_time, time_stamp)-> int:
        """

        Args:

        Returns:
            int

        """

        
        return server_time - time_stamp

    def is_minimum_waiting_time_has_passed (server_time, time_stamp, time_threshold)-> bool:
        """

        Args:

        Returns:
            bool

        """
        
        return delta_time (server_time, time_stamp) > time_threshold

    def is_send_additional_order_allowed (notional: float,
                                ask_price: float,
                                bid_price: float,
                                current_outstanding_order_len,
                                len_my_trades_open_sqlite_main_strategy,
                                max_size_my_trades_open_sqlite_main_strategy,
                                selected_transaction: list,
                                max_time_stamp,
                                strategy_attributes: list,
                                pct_threshold: float,
                                server_time: int
                                ) -> dict:
        """

        Args:

        Returns:
            dict

        """

        # transform to dict
        transaction= selected_transaction[0]    
        
        order_allowed= current_outstanding_order_len== 0  \
            and selected_transaction !=[] 
            
        if order_allowed:

            MAX_FACTOR= 3
            
            transaction= selected_transaction[0]
            
            # get transaction parameters
            params= get_basic_opening_paramaters(notional)
            
            # get transaction label and update the respective parameters
            label_main= strategy_attributes['strategy']
            transaction_side= transaction['direction']
            label_open = hedging_spot.get_label ('open', label_main) 
            params.update({"label": label_open})
            params.update({"instrument": transaction['instrument_name']})
            
            params.update({"side": strategy_attributes['side']})
            
            size_adjusted= size_adjustment(len_my_trades_open_sqlite_main_strategy, MAX_FACTOR)
            
            params["size"]= max(1, (int(max_size_my_trades_open_sqlite_main_strategy * size_adjusted)))
            print (f'len_transaction {len_my_trades_open_sqlite_main_strategy} size_adjusted {size_adjusted} {params}')
                
            if size_adjusted== 0:
                ONE_MINUTE= 60000
                WAITING_MINUTE= 60
                time_multiply= max(1, len_my_trades_open_sqlite_main_strategy - MAX_FACTOR)
                time_threshold: float =  time_multiply * ONE_MINUTE * WAITING_MINUTE
                minimum_waiting_time_has_passed= is_minimum_waiting_time_has_passed (server_time, 
                                                                                    max_time_stamp, 
                                                                                    time_threshold)
                AVG_PCT= 1/100 * time_multiply
                transaction_price= transaction['price']
                        
                if transaction_side=='sell':
                    averaging_price_reached= hedging_spot.is_transaction_price_plus_above_threshold(transaction_price,
                                                                                ask_price,
                                                                                AVG_PCT
                                                                                )
                    
                    params.update({"entry_price": bid_price})
                    
                if transaction_side=='buy':
                    
                    averaging_price_reached= hedging_spot.is_transaction_price_minus_below_threshold(transaction_price,
                                                                                bid_price,
                                                                                AVG_PCT
                                                                                )
                print (f'minimum_waiting_time_has_passed {minimum_waiting_time_has_passed} time_threshold {time_threshold} {time_multiply} transaction_price {transaction_price} averaging_price_reached {averaging_price_reached} ')
                
                if minimum_waiting_time_has_passed and averaging_price_reached:
                    order_allowed= True
                else:
                    order_allowed= False
                
            else:    
                if transaction_side =='sell':
                    params.update({"entry_price": ask_price})
                    
                    transaction_price_exceed_threshold = hedging_spot.is_transaction_price_plus_above_threshold (transaction['price'], 
                                                                                                                ask_price,
                                                                                                                pct_threshold) 
                    if transaction_price_exceed_threshold== False :
                        order_allowed= False
                        
                if transaction_side=='buy':
                    params.update({"entry_price": bid_price})
                    
                    transaction_price_exceed_threshold = hedging_spot.is_transaction_price_minus_below_threshold (transaction['price'], 
                                                                                                                bid_price, 
                                                                                                                pct_threshold) 
                    if transaction_price_exceed_threshold== False :
                        order_allowed= False
                
                print (f'len_transaction {len_my_trades_open_sqlite_main_strategy} transaction_price_exceed_threshold {transaction_price_exceed_threshold}')
        
        return dict(order_allowed= order_allowed,
                    order_parameters= [] if order_allowed== False else params)