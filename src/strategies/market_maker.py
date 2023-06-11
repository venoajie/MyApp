# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from strategies import hedging_spot
from strategies.basic_strategy import BasicStrategy 

@dataclass(unsafe_hash=True, slots=True)
class MarketMaker(BasicStrategy):

    """ """

    def get_basic_params(self) -> dict:
        """
        """
        return BasicStrategy(self.strategy_label)

    async def is_send_and_cancel_open_order_allowed (self,
                                          notional: float,
                                          ask_price: float,
                                          bid_price: float,
                                          server_time: int
                                          ) -> dict:
        """

        Args:

        Returns:
            dict

        """
        strategy_config= self.get_basic_params().get_strategy_config()
        
        orders_label_strategy= await self.get_basic_params().get_orders_attributes(self.strategy_label)
        print (f'orders_label_strategy {orders_label_strategy}')
        open_orders_label_strategy= [] if orders_label_strategy == [] else\
            [o for o in orders_label_strategy if 'open' in o["label_main"] ]
            
        print (f'open_orders_label_strategy {open_orders_label_strategy}')
        
        len_orders= open_orders_label_strategy['transactions_len']
        my_trades= await self.get_basic_params().get_my_trades_attributes(self.strategy_label)
        len_my_trades= my_trades['transactions_len']
        max_tstamp_my_trades= my_trades['max_time_stamp']
        
        params= self.get_basic_params().get_basic_opening_paramaters(notional)
        time_interval= params['interval_time_between_order_in_ms']
        
        order_allowed= False
        cancel_allowed= False
        
        if len_orders !=[] and len_orders > 0:
            max_tstamp_orders= open_orders_label_strategy['max_time_stamp']
            
            minimum_waiting_time_has_passed=  self.get_basic_params().is_minimum_waiting_time_has_passed (server_time, 
                                                                                                        max_tstamp_orders, 
                                                                                                        time_interval)
            if minimum_waiting_time_has_passed:
                cancel_allowed= True
        
        
        print (f'my_trades {my_trades}')
        
        if max_tstamp_my_trades == []:
            if len_orders== [] and len_my_trades== []:
                order_allowed= True
                    
        else:
            time_interval_qty= time_interval * len_my_trades
            
            minimum_waiting_time_has_passed=  self.get_basic_params().is_minimum_waiting_time_has_passed (server_time, 
                                                                                                        max_tstamp_my_trades, 
                                                                                                        time_interval_qty)

            if minimum_waiting_time_has_passed and len_orders== [] :
                order_allowed= True
                
        if order_allowed== True:
            
            if strategy_config['side']=='sell':
                params.update({"entry_price": ask_price})
            if strategy_config['side']=='buy':
                params.update({"entry_price": bid_price})

            params.update({"side": strategy_config['side']})
            
            # get transaction label and update the respective parameters
            label_open = self.get_basic_params().get_label ('open', self.strategy_label) 
            params.update({"label": label_open})
        
        return dict(order_allowed= order_allowed,
                    order_parameters= [] if order_allowed== False else params,
                    cancel_allowed= cancel_allowed,
                    cancel_id= open_orders_label_strategy['order_id_max_time_stamp'])
        
    def is_send_exit_order_allowed (self,
                                          ask_price: float,
                                          bid_price: float,
                                          selected_transaction: list
                                          ) -> dict:
        """
        """
        return self.get_basic_params().is_send_exit_order_allowed(ask_price, bid_price, selected_transaction)
        