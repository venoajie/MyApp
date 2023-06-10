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
        
        return [o for o in params if self.strategy_label in o["strategy"]]  [0]

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
    
    async def transaction_attributes (self, table) -> list:
        """ """

        result=  await self.querying_label_and_size(table)
        result_strategy_label= [o for o in result if o["label_main"] == self.strategy_label]
        
        return dict(
            transactions= result,
            max_time_stamp= [] if result_strategy_label  == [] else max(
                [o['timestamp'] for o in result_strategy_label ]
                ),
            transactions_sum= [] if result_strategy_label ==  [] else sum(
                [o['amount_dir'] for o in result_strategy_label]
                ),
            transactions_len=  [] if result_strategy_label ==  [] else len(
                [o  for o in result_strategy_label]
                )
            )  
        
    async def get_my_trades_attributes (self) -> list:
        """ """

        # get current size
        return await self.transaction_attributes('my_trades_all_json')
    
    async def get_orders_attributes (self) -> list:
        """ """

        # get current orders
        return await self.transaction_attributes('orders_all_json')    
        
        
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
    