#!/usr/bin/python3

# built ins
import asyncio
#import orjson
import cachetools.func

# installed
from dataclassy import dataclass
from loguru import logger as log

# user defined formula
import deribit_get
from transaction_management.deribit import open_orders_management, myTrades_management
from utilities import pickling, system_tools, string_modification as str_mod
from configuration import label_numbering, config
from strategies import entries_exits
from db_management import sqlite_management
# from market_understanding import futures_analysis

async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)

def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)

@dataclass(unsafe_hash=True, slots=True)
class GridPerpetual:

    """ """
    my_trades_open: list
    orders_from_sqlite: list

    async def get_strategy_from_active_trade_item (self) -> list:
        """
        """
        result = [o['label'] for o in self.active_trade_item][0]
        return dict(
            main= str_mod.parsing_label(result)['main'],
            transaction_net= str_mod.parsing_label(result)['transaction_net'])
        
    async def get_trades_as_per_label(self, active_trade_item, strategy_from_config) -> list:
        """
        self.strategy_from_config == None: for new order
        self.active_trade_item == None: for closing order
        """
        result = []
        try:
            if self.my_trades_open != []:
                if strategy_from_config == None:
                    label_main = str_mod.parsing_label ([o['label'] for o in active_trade_item][0]) ['main']

                    result =([
                    o for o in self.my_trades_open  ['all'] \
                        if  str_mod.parsing_label(o['label_main'])['main'] == label_main 
                        ]
                            )
                    
                if active_trade_item == None \
                    or active_trade_item == []:
                    result =([
                    o for o in self.my_trades_open ['all'] \
                        if  str_mod.parsing_label(o['label_main'])['main'] == strategy_from_config
                        ]
                            )
        except Exception as error:
            catch_error(error)

        return result

    async def get_params_orders_closed(self, active_trade_item) -> list:
        """
        """
        params_order = {}
        strategies = entries_exits.strategies
        
        # fetch strategies attributes
        if active_trade_item != None \
            or active_trade_item == []:
                
            trade_item = active_trade_item[0]
            side_transaction = trade_item['direction'] 
            price_transaction = trade_item['price'] 
            label_transaction = trade_item['label'] 
            
            strategy_label_int = str_mod.parsing_label(label_transaction)['int']
            strategy_label_transaction_status = str_mod.parsing_label(label_transaction)['transaction_status']
            strategy_label_main = str_mod.parsing_label(label_transaction)['main']
            strategy_attr = [
                            o for o in strategies if o["strategy"] == strategy_label_main
                        ][0]

            price_threshold =  price_transaction * strategy_attr["take_profit_pct"] 
            
            label_closed = f"{strategy_label_main}-closed-{strategy_label_int}"
            params_order.update({"label": label_closed})
                    
            if side_transaction == "buy":
                side = "sell"
                price_threshold =  price_transaction - price_threshold
            if side_transaction == "sell":
                side = "buy"
                price_threshold = price_transaction + price_threshold

            len_order = await self. open_orders_as_per_main_label(strategy_label_main)
            params_order.update({"price_threshold": price_threshold})
            params_order.update({"side": side})
            params_order.update({"size": trade_item['amount']})
            params_order.update({"len_order_limit": len_order})
            params_order.update({"type": 'limit'})
            params_order.update({"instrument": trade_item['instrument_name']})
            
        return params_order


    async def get_params_orders_open(self, strategy_label, notional) -> list:
        """
        """
        params_order = {}
        strategies = entries_exits.strategies

        params_order = {}  
        strategy_attr = [
                            o for o in strategies if o["strategy"] == strategy_label
                        ][0]
        

        size = int(abs(strategy_attr["equity_risked_pct"]  * notional))
        params_order.update({"side": strategy_attr["side"]})
        params_order.update({"size": max(1,size)})
        params_order.update({"type": "limit"})
        params_order.update({"len_order_limit": await self.open_orders_as_per_main_label (strategy_label)})
        
        return params_order
    
    async def open_orders_as_per_main_label (self, label_main) -> list:
        """
        """
        return 0 if self.orders_from_sqlite == [] \
            else len([o['label_main'] for o in self.orders_from_sqlite  ['all'] \
                if  str_mod.parsing_label(o['label_main'])['transaction_status'] == str_mod.parsing_label(label_main) ['transaction_status']
                        ])
                            
    async def provide_params_for_order(self) -> list:
        """
        """

        result = {}
        try:
            if self.my_trades_open != []:
                if self.strategy_from_config == None:
                    label_main = str_mod.parsing_label ([o['label'] for o in self.active_trade_item][0]) ['main']
                    print (label_main)
                    result =([
                    o for o in self.my_trades_open  ['all'] \
                        if  str_mod.parsing_label(o['label_main'])['main'] == label_main 
                        ]
                            )
                    
                if self.active_trade_item == None \
                    or self.active_trade_item == []:
                    result =([
                    o for o in self.my_trades_open ['all'] \
                        if  str_mod.parsing_label(o['label_main'])['main'] == self.strategy_from_config
                        ]
                            )
        except Exception as error:
            catch_error(error)

        return result    
    async def is_send_close_order_allowed(self) -> list:
        """
        """
        pass
    
    async def is_cancel_current_order_allowed(self) -> list:
        """
        """
        pass