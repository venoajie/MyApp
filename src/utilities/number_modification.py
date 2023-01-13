# -*- coding: utf-8 -*-

def net_position (selected_transactions: list)-> float:
    
    '''
    net sell: negative, net buy: positive
    
    '''    

    if selected_transactions != []:
        none_data = [[], None]
        
        try:

            sum_sell = sum([o['amount'] for o in selected_transactions if o['direction']=='sell'  ]) # sell = + sign
            sum_buy = sum([o['amount'] for o in selected_transactions if o['direction']=='buy'  ])
            #! -1 + 1 = 0, -10+10 = 0, [] = 0, None = 0. [] = No transcations, diff with net = 0 (could affect to leverage)
            #! solution = made another controls for leverage/modify output
            return [] if selected_transactions in none_data else  sum_buy - sum_sell
        
        except:
            return [] if selected_transactions in none_data else ([o['size'] for o in selected_transactions ]) [0] # sell = (-) sign
    

