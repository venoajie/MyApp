
"""
https://quant.stackexchange.com/questions/9527/is-price-gaping-the-major-risk-that-market-maker-has

""" 

def compute_individual_loss(ask_price: float,
                            bid_price: float,
                            side: str,
                            acquisition_cost: float) -> dict:
    """


    """ 
    if side== 'sell':
        loss_in_usd= acquisition_cost - bid_price
    
    if side== 'buy':
        loss_in_usd= ask_price - acquisition_cost
    
    return loss_in_usd