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

        Args:

        Returns:
            dict

        """
        
        #provide placeholder for params
        params= {}
        
        # default type: limit
        params.update({"type": 'limit'})
        
        strategy_label= self.strategy_label
        strategy_config= self.get_strategy_config()
        strategy_config_label= strategy_config['strategy']
        take_profit_pct_daily= strategy_config['take_profit_pct_daily']
        take_profit_pct_transaction= strategy_config['take_profit_pct']
                                                                        
        if strategy_label in strategy_config_label:
                
            hourly_qty= position_sizing.hourly_sizing_for_perpetual_grid(notional, 
                                                                        take_profit_pct_daily, 
                                                                        take_profit_pct_transaction
                                                                        )
            
            params.update({"size": position_sizing.quantities_per_order(hourly_qty)
                        }
                        )
        return params

    async def querying_label_and_size(table) -> dict:
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
        
    async def get_my_trades (self) -> list:
        """ """

        # get current size
        return await self.querying_label_and_size('my_trades_all_json')
    
    async def get_my_orders (self) -> list:
        """ """

        # get current orders
        return await self.querying_label_and_size('orders_all_json')