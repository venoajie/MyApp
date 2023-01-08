# # -*- coding: utf-8 -*-



from loguru import logger as log

def acquisition_cost (qty_bought: float, 
                      entry_price: float
                      )-> float:
    return qty_bought * entry_price

def price_difference (target_price: float, 
                      entry_price: float
                      )-> float:
    return (target_price - entry_price)/entry_price

def max_loss_allowed (capital: float, 
                      pct_loss: float=1/100
                      )-> float:
    return  (capital * pct_loss)

def pos_sizing (target_price: float, 
                entry_price: float, 
                capital: float, 
                pct_loss: float=1/10
                )-> float:
    
    return int(abs((max_loss_allowed (capital, pct_loss) / price_difference (entry_price, target_price))))


if __name__ == "__main__":
        
    PCT=1/100
    pct_loss= 1 * PCT
    current_price =1263
    stop_loss=1261
    capital_usd=100
    min_qty = 10
    max_loss = pct_loss * capital_usd
    distance_entry_stopLoss = (current_price - stop_loss)/current_price
    position_sizing =(max_loss / distance_entry_stopLoss)
    pos_sizing = pos_sizing (stop_loss, current_price,capital_usd, pct_loss)
    max_loss_allowed = max_loss_allowed (capital_usd, pct_loss)
    proof  = pos_sizing * distance_entry_stopLoss 

    log.warning (f'{max_loss=} {max_loss_allowed=} {distance_entry_stopLoss=}  {position_sizing=} {pos_sizing=} {proof=}')
