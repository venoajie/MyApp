# # -*- coding: utf-8 -*-

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
from risk_management import position_sizing
from db_management import sqlite_management

@dataclass(unsafe_hash=True, slots=True)
class BasicStrategy:

    """ """

    strategy_label: str

    def get_strategy_config(self) -> dict:
        """
        """
        from strategies import entries_exits
        
        params= entries_exits.strategies
        
        try:
            str_config= [o for o in params if self.strategy_label in o["strategy"]]  [0]
        
        except:
            from utilities import string_modification as str_mod
            
            str_config= [o for o in params if str_mod.parsing_label(self.strategy_label )['main']  in o["strategy"]]  [0]
        
        print (f' str_config {str_config}')
        
        return str_config

    def get_basic_opening_paramaters(self, notional: float= None) -> dict:
        """
        """
        
        #provide placeholder for params
        params= {}
        
        # default type: limit
        params.update({"type": 'limit'})
        
        strategy_config= self.get_strategy_config()
        strategy_config_label= strategy_config['strategy']
        
        take_profit_pct_daily= strategy_config['take_profit_pct_daily']
        take_profit_pct_transaction= strategy_config['take_profit_pct']
                                                                        
        if 'marketMaker' in strategy_config_label:
                
            qty_order_and_interval_time= position_sizing.qty_order_and_interval_time(notional, 
                                                                               take_profit_pct_daily, 
                                                                               take_profit_pct_transaction
                                                                               )
            
            params.update({"size": qty_order_and_interval_time['qty_per_order']
                        }
                        )
            params.update({"interval_time_between_order_in_ms": qty_order_and_interval_time['interval_time_between_order_in_ms']
                        }
                        )
        return params

    async def querying_label_and_size(self, table) -> dict:
        """
        """
        
        # execute query
        return  await sqlite_management.executing_label_and_size_query (table)

    def reading_from_db(self, end_point, instrument: str = None, status: str = None
    ) -> float:
        """ """
        from utilities import pickling, system_tools
        return pickling.read_data(
            system_tools.provide_path_for_file(end_point, instrument, status)
        )
    
    async def transaction_attributes (self, table, label_filter: str=None) -> list:
        """ """

        result=  await self.querying_label_and_size(table)
        result_strategy_label= [o for o in result if o["label_main"] == self.strategy_label]
        if label_filter != None:
            result_strategy_label= [o for o in result_strategy_label if label_filter in o["label_main"] ]
        max_time_stamp= [] if result_strategy_label  == [] else max(
            [o['timestamp'] for o in result_strategy_label ][0]
                )
        order_id_max_time_stamp= [] if max_time_stamp  == []  else\
            [o["order_id"] for o in result_strategy_label if o["timestamp"] == max_time_stamp][0]
        return dict(
            transactions= result,
            max_time_stamp= max_time_stamp,
            order_id_max_time_stamp= order_id_max_time_stamp,
            transactions_sum= [] if result_strategy_label ==  [] else sum(
                [o['amount_dir'] for o in result_strategy_label]
                ),
            transactions_len=  [] if result_strategy_label ==  [] else len(
                [o  for o in result_strategy_label]
                )
            )  
        
    async def get_my_trades_attributes (self, label_filter: str=None) -> list:
        """ """

        # get current size
        return await self.transaction_attributes('my_trades_all_json', label_filter)
    
    async def get_orders_attributes (self, label_filter: str=None) -> list:
        """ """

        # get current orders
        return await self.transaction_attributes('orders_all_json', label_filter)    
        
        
    def delta_time (self, server_time, time_stamp)-> int:
        """

        """

        
        return server_time - time_stamp

    def is_minimum_waiting_time_has_passed (self, server_time, time_stamp, time_threshold)-> bool:
        """


        """
        
        return self.delta_time (server_time, time_stamp) > time_threshold

    def get_label (self, status: str, label_main_or_label_transactions: str) -> str:
        """
        """
        
        from configuration import label_numbering
        
        if status=='open':
            # get open label
            label = label_numbering.labelling("open", label_main_or_label_transactions)
        
        if status=='closed':
            from utilities import string_modification as str_mod
            
            # parsing label id
            label_id= str_mod.parsing_label(label_main_or_label_transactions)['int']

            # parsing label strategy
            label_main= str_mod.parsing_label(label_main_or_label_transactions)['main']
            
            # combine id + label strategy
            label = f'''{label_main}-closed-{label_id}'''
            
        return label
    
    def get_basic_closing_paramaters(self, 
                                     selected_transaction: list) -> dict:
        """

        Args:

        Returns:
            dict

        """
        transaction= selected_transaction[0]
        
        #provide placeholder for params
        params= {}
        
        # default type: limit
        params.update({"type": 'limit'})
        
        # size=exactly amount of transaction size
        params.update({"size": transaction['amount']})
        
        # determine side
        transaction_side= transaction['direction']
        if transaction_side=='sell':
            params.update({"side": 'buy'})
        if transaction_side=='buy':
            params.update({"side": 'sell'})
            
        label_closed = self.get_label ('closed', transaction['label']) 
        params.update({"label": label_closed})
        
        return params

    def pct_price_in_usd(self, price: float, pct_threshold: float)-> bool:    
        return price * pct_threshold

    def price_plus_pct(self, price: float, pct_threshold: float)-> float:    
        return price + self.pct_price_in_usd (price, pct_threshold)

    def price_minus_pct(self, price: float, pct_threshold: float)-> float:    
        return price - self.pct_price_in_usd (price, pct_threshold)

    def is_transaction_price_minus_below_threshold(self, 
                                                   last_transaction_price: float,
                                                   current_price: float,
                                                   pct_threshold: float
                                                   )-> bool:    
        
        return self.price_minus_pct (last_transaction_price, pct_threshold) > current_price

    def is_transaction_price_plus_above_threshold(self, 
                                                  last_transaction_price: float,
                                                  current_price: float,
                                                  pct_threshold: float
                                                )-> bool:  
        
        return self.price_plus_pct (last_transaction_price, pct_threshold) < current_price

    async def is_send_exit_order_allowed (self,
                                    ask_price: float,
                                    bid_price: float,
                                    selected_transaction: list,
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
        
        strategy_config= self.get_strategy_config()

        # get take profit pct
        tp_pct= strategy_config["take_profit_pct"]

        # get transaction parameters
        params= self.get_basic_closing_paramaters(selected_transaction)
        
        if transaction_side=='sell':
            tp_price_reached= self.is_transaction_price_minus_below_threshold(last_transaction_price,
                                                                        bid_price,
                                                                        tp_pct
                                                                        )
            params.update({"entry_price": bid_price})
            
        if transaction_side=='buy':
            tp_price_reached= self.is_transaction_price_plus_above_threshold(last_transaction_price,
                                                                        ask_price,
                                                                        tp_pct
                                                                        )
            params.update({"entry_price": ask_price})
        
        orders= await self.get_orders_attributes()
        len_orders= orders['transactions_len']
        print(f'tp_price_reached {tp_price_reached}')
        no_outstanding_order= len_orders < 1

        order_allowed= tp_price_reached\
                and no_outstanding_order 
        
        if order_allowed:
            
            params.update({"instrument":  transaction['instrument_name']})
            
        return dict(order_allowed= order_allowed,
                    order_parameters= [] if order_allowed== False else params)