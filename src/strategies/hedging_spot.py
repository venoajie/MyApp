# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from strategies.basic_strategy import BasicStrategy 

@dataclass(unsafe_hash=True, slots=True)
class HedgingSpot(BasicStrategy):

    """ """

    def get_basic_params(self) -> dict:
        """
        """
        return BasicStrategy(self.strategy_label)

    def are_size_and_order_appropriate_for_ordering (self,
                                                     notional: float,
                                                    current_size: float,
                                                    current_outstanding_order_len: int
                                                    )-> bool:
        """

        """   
        return abs(current_size) < notional and current_outstanding_order_len== 0
    
    async def is_send_and_cancel_open_order_allowed (self,
                                                     notional: float,
                                                     ask_price: float,
                                                     server_time: int,
                                                     threshold: float= 30
                                                     ) -> dict:
        """

        """
        
        open_orders_label_strategy: dict= await self.get_basic_params().get_orders_attributes('open')
        
        len_orders: int= open_orders_label_strategy['transactions_len']
        my_trades: dict= await self.get_basic_params().get_my_trades_attributes()
        sum_my_trades: int= my_trades['transactions_sum']
        params: dict= self.get_basic_params().get_basic_opening_paramaters(notional,
                                                                     ask_price,
                                                                     None)
        
        order_allowed: bool= self.are_size_and_order_appropriate_for_ordering (notional,
                                                                         sum_my_trades,
                                                                         len_orders
                                                                         )
        cancel_allowed: bool= False
        
        if len_orders !=[] and len_orders > 0:
            ONE_MINUTE: int = 60000
            time_interval= ONE_MINUTE* threshold
            max_tstamp_orders: int= open_orders_label_strategy['max_time_stamp']
            
            minimum_waiting_time_has_passed: bool=  self.get_basic_params().is_minimum_waiting_time_has_passed (server_time, 
                                                                                                                max_tstamp_orders, 
                                                                                                                time_interval)
            if minimum_waiting_time_has_passed:
                cancel_allowed: bool= True
                
        return dict(order_allowed= order_allowed,
                    order_parameters= [] if order_allowed== False else params,
                    cancel_allowed= cancel_allowed,
                    cancel_id= open_orders_label_strategy['order_id_max_time_stamp'])
            
    def hedged_value_to_notional (self,
                                  notional: float, 
                                  hedged_value: float
                                  ) -> float:
        """ 
        """        
        print(f'notional {notional}')
        print(f'hedged_value {hedged_value}')
        return abs(hedged_value/notional)

    def is_hedged_value_to_notional_exceed_threshold (self,
                                                      notional: float, 
                                                      hedged_value: float, 
                                                      threshold : float
                                                      ) -> float:
        """ 
        """        
        return self.hedged_value_to_notional (notional, hedged_value) > threshold
    
    async def is_send_exit_order_allowed (self,
                                    notional: float,
                                    ask_price: float,
                                    bid_price: float,
                                    selected_transaction: list,
                                    MIN_HEDGING_RATIO: float= .8
                                    ) -> dict:
        """
        """        
        my_trades: dict= await self.get_basic_params().get_my_trades_attributes()
        sum_my_trades: int= my_trades['transactions_sum']
        
        hedged_value_is_still_safe: bool= self.is_hedged_value_to_notional_exceed_threshold (notional,
                                                                                  sum_my_trades,
                                                                                  MIN_HEDGING_RATIO)
        exit_params: dict= self.get_basic_params().is_send_exit_order_allowed(ask_price, 
                                                                  bid_price, 
                                                                  selected_transaction
                                                                  )
        
        open_orders_label_strategy: dict= await self.get_basic_params().get_orders_attributes('open')
        
        len_orders: int= open_orders_label_strategy['transactions_len']
        
        no_outstanding_order: bool= len_orders < 1
        
        exit_allowed: bool=   exit_params['order_allowed']  \
            and hedged_value_is_still_safe \
            and no_outstanding_order                                                     
                                                                              
        return dict(order_allowed= exit_allowed,
                    order_parameters= [] if exit_allowed== False else exit_params['order_parameters'])
        