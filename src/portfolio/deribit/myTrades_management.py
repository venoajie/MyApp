# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass

@dataclass(unsafe_hash=True, slots=True)
class MyTrades ():

    '''
        
    +----------------------------------------------------------------------------------------------+ 
    #  clean up my trades data
    '''       
    my_trades: list
            
    def my_trades_api (self):
        
        '''
        '''    
        return [o for o in self.my_trades if o['api'] == True]
    
    def my_trades_manual (self):
        
        '''
        '''    
        return [o for o in self.my_trades if o['api'] == False]