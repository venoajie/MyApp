# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from loguru import logger as log

from utilities import string_modification
from portfolio.deribit import myTrades_management

@dataclass(unsafe_hash=True, slots=True)
class RunningStrategies ():

    '''
    '''       
    strategy: list = []
    index_price: list = []
    my_trades_open: list = []
    my_orders_api_basedOn_label_strategy: list = []
    notional: float = []
    instrument: float = []
    
    def strategy_attributes (self) -> dict:
        
        '''
        '''  
        one_minute =  60000                
        return {'equity_risked': self.strategy ['equity_risked'] ,
                'pct_threshold_TP': self.strategy ['take_profit'],
                'pct_threshold_CL': self.strategy ['cut_loss'],
                'side': self.strategy ['side'],
                'averaging': self.strategy ['averaging'],
                'label_strategy': self.strategy ['strategy'],
                'entry_price': self.strategy ['entry_price'],
                'halt_minute_before_reorder': self.strategy ['halt_minute_before_reorder'] * one_minute ,
                } 
        
    def my_trades_direction  (self) -> list:
        
        '''
        '''  

        return {'sell': [o  for o in self.my_trades_open if o['direction'] == 'sell'],
                'buy': [o  for o in self.my_trades_open if o['direction'] == 'buy'] 
                } 
        
    def my_orders_direction (self) -> list:
        
        '''
        '''  

        return {'sell': []  if self.my_orders_api_basedOn_label_strategy == [] \
                            else ([o  for o in self. my_orders_api_basedOn_label_strategy if o['direction'] == 'sell']),
                'buy': []  if self.my_orders_api_basedOn_label_strategy == [] \
                            else ([o  for o in self.my_orders_api_basedOn_label_strategy if o['direction'] == 'buy'] )
                } 
                
    def closed_strategy (self) -> list:
        
        '''
        '''  

        open_orders_buy = self.my_orders_direction () ['buy'] 
        open_orders_sell = self.my_orders_direction () ['sell'] 
        
        if self.my_trades_open !=[]:
            
            my_trades_sell = self.my_trades_direction () ['sell'] 
            my_trades_buy = self.my_trades_direction () ['buy'] 
            
            for my_trades in self.my_trades_open:
                #log.warning (self.strategy_attributes () )
                log.warning (my_trades )
                
                price  = my_trades ['price']  
                label = self.strategy_attributes  () ['label_strategy']      
                size  = my_trades['amount']  
                direction  = my_trades ['direction']  
                instrument  = my_trades ['instrument_name'] 
                label_open_numbered =  my_trades ['label'] 
                label_int = string_modification.extract_integers_from_text (label_open_numbered)      
                label_closed_numbered  = f'{label}-closed-{label_int}'
                        
                #! CLOSED ORDER SELL
                if len (my_trades_sell) != 0 \
                    and len (open_orders_buy)==0 \
                        and direction == 'sell':
                            
                    tp_price = price - (price * self.strategy_attributes  ()['pct_threshold_TP'])
                    cl_price = price + (price * self.strategy_attributes  () ['pct_threshold_CL'])
                    send_order = tp_price < self.index_price or cl_price > self.index_price
                    side = 'buy'
                    
                #! CLOSED ORDER BUY
                if len (my_trades_buy) != 0 \
                    and len (open_orders_sell)==0 \
                        and direction == 'buy':
                            
                    tp_price = price + (price * self.strategy_attributes  () ['pct_threshold_TP'])
                    cl_price = price - (price * self.strategy_attributes  () ['pct_threshold_CL'])
                    send_order = tp_price > self.index_price or cl_price < self.index_price   
                    side = 'sell'          
                        
                log.critical (f'CLOSE SD  {send_order=} {instrument=} {side=} {direction=} {size=} {tp_price=} {cl_price=} {label_open_numbered=} {label_closed_numbered=}')
                
                return {'send_order': send_order,
                        'instrument': instrument,
                        'side': side, 
                        'size': size, 
                        'label_numbered': label_closed_numbered
                        }
                     
    def open_strategy (self) -> list:
        
        '''
        '''  
        from configuration import  label_numbering
        from risk_management import position_sizing

        open_orders_buy = self.my_orders_direction () ['buy'] 
        open_orders_sell = self.my_orders_direction () ['sell'] 
        label_strategy:str = self.strategy_attributes () ['label_strategy']
        
        my_trades_buy = self.my_trades_direction () ['buy'] 
        my_trades_sell = self.my_trades_direction () ['sell'] 
        side:str =  self.strategy_attributes  () ['side']
        entry_price:str =  self.strategy_attributes  () ['entry_price']
        equity_risked:str =  self.strategy_attributes  () ['equity_risked']
        pct_threshold_CL:str =  self.strategy_attributes  () ['pct_threshold_CL']
        label_numbered: str = label_numbering.labelling ('open', label_strategy)
        
        log.debug (f'OPEN  {my_trades_buy=} {my_trades_sell=}')
        log.warning (f'OPEN  {open_orders_buy=} {open_orders_sell=}')
        
        size: float = position_sizing.pos_sizing (pct_threshold_CL,
                                                  entry_price, 
                                                  self.notional, 
                                                  equity_risked
                                                  )   
        
        if my_trades_buy ==[] \
            and open_orders_buy ==[]:
                
            send_order:bool =  True
        
        if my_trades_sell ==[] \
            and open_orders_sell ==[]:
                
            send_order:bool =  True
            
        log.critical (f'OPEN  {send_order=} {self.instrument=} {side=} {size=} {label_numbered=}')
        #log.debug (f' {my_trades_buy=} {my_trades_sell=}')
        log.debug (f' {open_orders_buy=} {open_orders_sell=}')
        
        return {'send_order': send_order,
                'instrument': self.instrument,
                'side': side, 
                'size': size, 
                'label_numbered': label_numbered
                }
    
def main (strategy,
          index_price,
          my_trades_open,
          my_orders_api_basedOn_label_strategy,
          notional,
          instrument
          ) -> None:
    
    '''
    '''
    #my_trades_open =  [o  for o in my_trades_open if o['direction'] == 'sell']
    my_trades_open_strategy = ([o  for o in my_trades_open if strategy['strategy'] in o['label']])
    my_orders_open_strategy = ([o  for o in my_orders_api_basedOn_label_strategy if strategy['strategy'] in o['label']])
    log.critical (my_trades_open_strategy)
    log.critical (my_orders_open_strategy)

    strategies = RunningStrategies (strategy,
                                    index_price,
                                    my_trades_open_strategy,
                                    my_orders_open_strategy,
                                    notional,
                                    instrument
                                    )
    
    return {'open_strategy': strategies. open_strategy (),
            'closed_strategy': strategies. closed_strategy ()}
