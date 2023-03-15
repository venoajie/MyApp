# # -*- coding: utf-8 -*-
'''
Compute:
- position sizing for each order send
- delta for current position
- leverage for current position
'''

def price_difference (cut_loss_price: float, 
                      entry_price: float
                      )-> float:
    
    '''
    Compute percentage difference between entry price vs cut loss price in USD
    
    Args:
        cut_loss_price (float)
        entry_price (float)
 
    Returns:
        float
    
    '''
    return (cut_loss_price - entry_price) / entry_price

def max_loss_allowed (capital: float, 
                      pct_loss: float=1/100*.5
                      )-> float:
    
    '''
    Compute maximum loss allowed in USD
    
    Args:
        capital (float)
        pct_loss (float). Default= .5%
 
    Returns:
        float
    
    '''   
    
    return  (capital * pct_loss)

def pos_sizing (cut_loss_price: float, 
                entry_price: float, 
                capital: float, 
                pct_loss: float=1/10
                )-> float:
        
    '''
    Compute position sizing for each order send
    
    Args:
        cut_loss_price (float)
        entry_price (float)
        capital (float)
        pct_loss (float)
 
    Returns:
        float
    
    Reference:
        https://
    '''
    return int(
        abs(
            (
                max_loss_allowed (capital, 
                                  pct_loss
                                  ) / price_difference (entry_price, 
                                                        cut_loss_price
                                                        )
                )
            )
        )

def compute_delta (notional: float, 
                   total_long_qty: int, 
                   total_short_qty: int
                   )-> float:
    
    '''
    Compute delta for current position
    
    Args:
        notional (float)
        total_short_qty (int)
        total_short_qty (int)
 
    Returns:
        float
    
    Reference:
        https://
        
    '''
    return (notional + total_long_qty + total_short_qty) /notional

def compute_leverage (notional: float, 
                      total_long_qty: int,
                      total_short_qty: int
                      )-> float:
    
    '''
    Compute leverage for current position
    
    Args:
        notional (float)
        total_short_qty (int)
        total_short_qty (int)
 
    Returns:
        float
    
    Reference:
        https://
    '''
    return (total_long_qty + abs(total_short_qty))/notional