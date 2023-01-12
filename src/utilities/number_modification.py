# -*- coding: utf-8 -*-

def net_position (selected_transactions: list)-> float:
    
    '''
    net sell: negative, net buy: positive
    '''    

    if selected_transactions != []:
        
        try:

            sum_sell = sum([o['amount'] for o in selected_transactions if o['direction']=='sell'  ]) # sell = + sign
            sum_buy = sum([o['amount'] for o in selected_transactions if o['direction']=='buy'  ])
            return 0 if selected_transactions == [] else  sum_buy - sum_sell
        
        except:
            return 0 if selected_transactions == [] else ([o['size'] for o in selected_transactions ]) [0] # sell = (-) sign
    

