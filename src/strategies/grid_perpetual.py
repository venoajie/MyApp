#!/usr/bin/python3

# built ins
import asyncio

# installed
from dataclassy import dataclass

# user defined formula
import deribit_get
from utilities import  system_tools, string_modification as str_mod
from strategies import entries_exits

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

    async def get_params_orders_closed(self, active_trade_item, best_bid_prc, best_ask_prc) -> list:
        """
        """
        params_order = {}
        strategies = entries_exits.strategies
        #print (f'active_trade_item {active_trade_item}')
        
        # fetch strategies attributes
        if active_trade_item != None \
            or active_trade_item != []:
                
            trade_item = active_trade_item[0]
            
            label_transaction = trade_item['label']
            
            strategy_label_main = str_mod.parsing_label(label_transaction)['main']

            strategy_attr = [o for o in strategies if o["strategy"] == strategy_label_main][0]

            side_transaction = trade_item['direction'] 
            price_transaction = trade_item['price'] 
            
            price_margin =  price_transaction * strategy_attr["take_profit_pct"] 
            
            #get label closed
            label_closed = await self.get_closed_label (label_transaction)
            params_order.update({"label": label_closed})
            
            #get qty open order per label
            open_orders_under_same_label_status = await self.open_orders_as_per_main_label (strategy_label_main)
            len_order_limit= open_orders_under_same_label_status['len_result']
            params_order.update({"len_order_limit": len_order_limit})
                    
            if side_transaction == "buy":
                side = "sell"
                price_threshold = price_transaction + price_margin
                order_buy = False
                order_sell = len_order_limit == 0 and best_ask_prc > price_threshold
                params_order.update({"entry_price": best_ask_prc})
                
            if side_transaction == "sell":
                side = "buy"
                price_threshold =  price_transaction - price_margin
                order_sell = False
                order_buy= len_order_limit == 0 and best_bid_prc < price_threshold
                params_order.update({"entry_price": best_bid_prc})
            
            params_order.update({"price_threshold": price_threshold})
            params_order.update({"side": side})
            params_order.update({"size": trade_item['amount']})
            
            params_order.update({"type": 'limit'})
            params_order.update({"instrument": trade_item['instrument_name']})
            params_order.update({"order_buy": order_buy})
            params_order.update({"order_sell": order_sell})
            
        return params_order

    async def get_params_orders_open(self, strategy_label, notional) -> list:
        """
        """
        params_order = {}
        strategies = entries_exits.strategies

        params_order = {}  
        strategy_attr = [ o for o in strategies if o["strategy"] == strategy_label][0]

        open_orders_under_same_label_status = await self.open_orders_as_per_main_label (strategy_label)
        size = int(abs(strategy_attr["equity_risked_pct"]  * notional))
        params_order.update({"side": strategy_attr["side"]})
        params_order.update({"size": max(1,size)})
        params_order.update({"type": "limit"})
        params_order.update({"len_order_limit": open_orders_under_same_label_status['len_result']})
        
        return params_order
    
    async def open_orders_as_per_main_label (self, label_main: str) -> list:
        """
        """
        result =  [] if self.orders_from_sqlite['list_data_only'] == [] \
            else ([o['label_main'] for o in self.orders_from_sqlite  ['all'] \
                if  str_mod.parsing_label(o['label_main'])['transaction_status'] == str_mod.parsing_label(label_main) ['transaction_status']
                        ])

        return dict(
            detail= result,
            len_result= 0 if result == [] else len (result))
    
    async def get_closed_label(self, label_transaction: str) -> str:
        """
        """

        strategy_label_int = str_mod.parsing_label(label_transaction)['int']
        strategy_label_main = str_mod.parsing_label(label_transaction)['main']
        
        return f"{strategy_label_main}-closed-{strategy_label_int}"
