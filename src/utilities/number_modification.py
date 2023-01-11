# -*- coding: utf-8 -*-

def net_position (selected_transactions: list)-> float:
    
    '''
    net sell: negative, net buy: positive
    '''    

    if selected_transactions != []:
        sum_sell = sum([o['amount'] for o in selected_transactions if o['direction']=='sell'  ])
        sum_buy = sum([o['amount'] for o in selected_transactions if o['direction']=='buy'  ])
            
    return 0 if selected_transactions == [] else  sum_buy - sum_sell

