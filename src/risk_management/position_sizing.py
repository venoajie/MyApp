# # -*- coding: utf-8 -*-

def acquisition_cost (qty_bought: float, 
                      entry_price: float
                      )-> float:
    return qty_bought * entry_price

def price_difference (target_price: float, 
                      entry_price: float
                      )-> float:
    return (target_price - entry_price)/entry_price

def max_loss_allowed (capital: float, 
                      pct_loss: float=1/100*.5
                      )-> float:
    return  (capital * pct_loss)

def pos_sizing (target_price: float, 
                entry_price: float, 
                capital: float, 
                pct_loss: float=1/10
                )-> float:
    
    return int(abs((max_loss_allowed (capital, pct_loss) / price_difference (entry_price, target_price))))


def compute_delta (notional: float, total_long: int, total_short: int)-> float:
    
    return (notional + total_long + total_short) /notional


def compute_leverage (notional: float, total_long: int, total_short: int)-> float:
    
    return (total_long + abs(total_short))/notional