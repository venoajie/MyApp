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
    
    
    def my_trades_api_basedOn_label (self, label: str)-> list:
        
        '''
        '''    
        #print(label)
        #print( self.my_trades_api ())
        #print(([o for o in self.my_trades_api () if  label in o['label'] ]))
        return [] if self.my_trades_api () == [] else  ([o for o in self.my_trades_api () if  label in o['label'] ])