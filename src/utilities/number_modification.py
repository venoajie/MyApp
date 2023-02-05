# -*- coding: utf-8 -*-

def net_position (selected_transactions: list)-> float:
    
    '''
    net sell: negative, net buy: positive
    
    '''    

    if selected_transactions != []:
        
        try:

            sum_sell = sum([o['amount'] for o in selected_transactions if o['direction']=='sell'  ]) # sell = + sign
            sum_buy = sum([o['amount'] for o in selected_transactions if o['direction']=='buy'  ])
            
            #! -1 + 1 = 0, -10+10 = 0, [] = 0, None = 0. [] = No transcations, diff with net = 0 (could affect to leverage)
            #! solution = made another controls for leverage/modify output/preventive
            return  sum_buy - sum_sell
        
        except:
            return  ([o['size'] for o in selected_transactions ]) [0] # sell = (-) sign
    
    else:    
        return selected_transactions
    
def get_nearest_tick (price: float, 
                      tick: float
                      )-> float:
    
    '''
    
    '''    
    len_tick = len (
        str(
            tick
            )
        )-2

    return round (
        (int (
            price/tick
            )
         ) * tick, 
                 len_tick
                 )

