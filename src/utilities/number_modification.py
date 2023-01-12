# -*- coding: utf-8 -*-

def net_position (selected_transactions: list)-> float:
    
    '''
    net sell: negative, net buy: positive
    '''    
    from loguru import logger as log

    if selected_transactions != []:
        
        try:
            log.critical (selected_transactions)
            sum_sell = sum([o['amount'] for o in selected_transactions if o['direction']=='sell'  ])
            sum_buy = sum([o['amount'] for o in selected_transactions if o['direction']=='buy'  ])
        except:
            log.debug (selected_transactions)
            sum_sell = sum([o['size'] for o in selected_transactions ])
            sum_buy = sum([o['size'] for o in selected_transactions])
            
    return 0 if selected_transactions == [] else  sum_buy - sum_sell

