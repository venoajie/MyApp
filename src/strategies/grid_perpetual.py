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

    async def get_params_orders_closed(self, active_trade_item, current_net_position_size, best_bid_prc, best_ask_prc) -> list:
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
            open_orders_under_same_label_status = await self.open_orders_as_per_main_label (label_transaction)
            len_order_limit= open_orders_under_same_label_status['len_result']
            size= trade_item['amount']
            params_order.update({"len_order_limit": len_order_limit})
                    
            if side_transaction == "buy":
                adj_tp= await self.adjusting_tp_closed_order(side_transaction, size, current_net_position_size) 
                price_margin =  price_transaction * strategy_attr["take_profit_pct"] * adj_tp
                side = "sell"
                price_threshold = price_transaction + price_margin
                order_buy = False
                order_sell = len_order_limit == 0 and best_ask_prc > price_threshold
                params_order.update({"entry_price": best_ask_prc})
                
            if side_transaction == "sell":
                adj_tp= await self.adjusting_tp_closed_order(side_transaction, size, current_net_position_size) 
                price_margin =  price_transaction * strategy_attr["take_profit_pct"]  * adj_tp
                side = "buy"
                price_threshold =  price_transaction - price_margin
                order_sell = False
                order_buy= len_order_limit == 0 and best_bid_prc < price_threshold
                params_order.update({"entry_price": best_bid_prc})
            
            params_order.update({"price_threshold": price_threshold})
            params_order.update({"side": side})
            params_order.update({"size": size})
            
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

    async def adjusting_size_open_order(self, current_side, current_proposed_size, current_net_position_size) -> float:
        """
        """
        #print (f' current_side {current_side}')
        #print (f' current_proposed_size {current_proposed_size}')
        #print (f' current_net_position_size {current_net_position_size}')

        if current_side == 'sell':
            
            net_size = abs(current_net_position_size - current_proposed_size)
            #print (f' sell net_size {net_size}')
            
            if current_net_position_size <=0 :
                new_size = current_proposed_size
                
            if current_net_position_size >0:
                if net_size == abs(current_proposed_size):
                    new_size = current_proposed_size
                elif abs(current_net_position_size) > abs(current_proposed_size):
                    new_size = int(max(current_proposed_size, current_proposed_size * 2, (net_size * 25/100)))
                else:
                    new_size = current_proposed_size
                
        if current_side == 'buy':
            
            net_size = abs(current_net_position_size + current_proposed_size)
            #print (f' buy net_size {net_size}')
            
            if current_net_position_size >= 0 :
                new_size = current_proposed_size
            if current_net_position_size <0:
                if  abs(current_net_position_size) == net_size:
                    new_size = current_proposed_size
                elif net_size > abs(current_proposed_size):
                    new_size = int(max(current_proposed_size, current_proposed_size * 2, (net_size * 25/100)))
                else:
                    new_size = current_proposed_size
        return new_size
    
    async def open_orders_as_per_main_label (self, label_main: str) -> list:
        """
        """
        result =  [] if self.orders_from_sqlite['list_data_only'] == [] \
            else ([o['label_main'] for o in self.orders_from_sqlite  ['all'] \
                if  str_mod.parsing_label(o['label_main'])['transaction_status'] == str_mod.parsing_label(label_main) ['transaction_status']
                        ])

        if str_mod.parsing_label(label_main) ['transaction_status'] == None:
            result =  [] if self.orders_from_sqlite['list_data_only'] == [] \
            else ([o['label'] for o in self.orders_from_sqlite  ['list_data_only'] \
                if  str_mod.parsing_label(o['label'])['main'] == str_mod.parsing_label(label_main) ['main'] ])
            
        #print (f' 151 label_main  {label_main}')
        #print (f' 152 open_orders_as_per_main_label  {result}')
        #print (self.orders_from_sqlite['list_data_only'])
        #print ([o  for o in self.orders_from_sqlite  ['all'] ])
        print (str_mod.parsing_label(label_main) ['transaction_status'])
        return dict(
            detail= result,
            len_result= 0 if result == [] else len (result))
    
    async def get_closed_label(self, label_transaction: str) -> str:
        """
        """

        strategy_label_int = str_mod.parsing_label(label_transaction)['int']
        strategy_label_main = str_mod.parsing_label(label_transaction)['main']
        
        return f"{strategy_label_main}-closed-{strategy_label_int}"

    async def adjusting_tp_closed_order(self, current_side, current_proposed_size, current_net_position_size) -> dict:
        """
        """
        if current_side == 'sell':
            
            net_size = abs(current_net_position_size - current_proposed_size)
            #print (f' sell net_size {net_size}')
            
            if current_net_position_size <=0 :
                tp_factor= 1
                
            if current_net_position_size >0:
                if net_size == abs(current_proposed_size):
                    tp_factor= 1
                elif abs(current_net_position_size) > abs(current_proposed_size):
                    tp_factor= 2
                else:
                    tp_factor= 1
                
        if current_side == 'buy':
            
            net_size = abs(current_net_position_size + current_proposed_size)
            print (f' buy net_size {net_size}')
            print (f' buy current_net_position_size {current_net_position_size}')
            print (f' buy net_size > abs(current_proposed_size) {net_size > abs(current_proposed_size)}')
            
            if current_net_position_size >= 0 :
                tp_factor= 1
            if current_net_position_size <0:
                if  abs(current_net_position_size) == net_size:
                    tp_factor= 1
                elif net_size > abs(current_proposed_size):
                    tp_factor= 2
                else:
                    tp_factor= 1
        return tp_factor
    
    
    async def adjusting_waiting_time_open_order(self, current_side, current_proposed_size, current_net_position_size) -> float:
        """
        """

        if current_side == 'sell':
            
            net_size = abs(current_net_position_size - current_proposed_size)
            #print (f' sell net_size {net_size}')
            
            if current_net_position_size <=0 :
                waiting_time_factor = 1
                
            if current_net_position_size >0:
                if net_size == abs(current_proposed_size):
                    waiting_time_factor = 1
                elif abs(current_net_position_size) > abs(current_proposed_size):
                    waiting_time_factor = 1
                else:
                    waiting_time_factor = 1
                
        if current_side == 'buy':
            
            net_size = abs(current_net_position_size + current_proposed_size)
            #print (f' buy net_size {net_size}')
            
            if current_net_position_size >= 0 :
                waiting_time_factor = 1
            if current_net_position_size <0:
                if  abs(current_net_position_size) == net_size:
                    waiting_time_factor = 1
                elif net_size > abs(current_proposed_size):
                    waiting_time_factor = 1
                else:
                    waiting_time_factor = 1
        return waiting_time_factor
    