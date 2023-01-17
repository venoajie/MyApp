# https://quant.stackexchange.com/questions/9527/is-price-gaping-the-major-risk-that-market-maker-has

# installed
from dataclassy import dataclass
from loguru import logger as log

from utilities import string_modification
from portfolio.deribit import myTrades_management

@dataclass(unsafe_hash=True, slots=True)
class LossLeadership ():

    '''
    '''       
    label: str 
    my_trades: list = []
                
    def apply_cut_loss_for_every_active_position (self) -> list:
        
        '''
        '''       
        #obtain all open orders
        # listing all of open trade
        for open_trade in self.my_trades:
            
            pass
    
        return   [] if self.my_trades  in none_data  else  ([o for o in self.my_trades if self.label in o['label']  ])