# -*- coding: utf-8 -*-
from src.risk_management import position_sizing

def test_pos_sizing():
    assert position_sizing.pos_sizing(target_price=100, entry_price=90, capital=1000, pct_loss = .5/100) == 50
    assert position_sizing.pos_sizing(target_price=90, entry_price=100, capital=1000, pct_loss = .5/100) == 45
    assert position_sizing.pos_sizing(target_price=100, entry_price=90, capital=1000, pct_loss = 1/100) == 100
    assert position_sizing.pos_sizing(target_price=90, entry_price=100, capital=1000, pct_loss = 1/100) == 90

    
def test_compute_delta  ():
    
    notional = 100
    long = 0
    short = -100
    compute_delta =  position_sizing.compute_delta(notional, long, short) 
    assert compute_delta == 0
    
def test_compute_leverage  ():
    
    notional = 100
    long = 0
    short = -100
    compute_delta =  position_sizing.compute_leverage(notional, long, short) 
    assert compute_delta == 1