#!/usr/bin/env python
# -*- coding: utf-8 -*-

strategies = [
    {
    'strategy': 'supplyDemandShort15',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'side': 'sell',
    'entry_price': 1538,
    'take_profit_usd': 1508.5,
    'take_profit_pct': 1/100,
    'quantity_discrete': 15,
    'cut_loss_usd': 1565.5,
    'cut_loss_pct': (1/100)/2,
    'averaging': 15,
    'halt_minute_before_reorder': 60, 
    'equity_risked_usd': 60, 
    'equity_risked_pct': 1/100
    },
    
    {
    'strategy': 'hedgingSpot',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'side': 900,
    'entry_price': 1000,
    'take_profit_usd': (1/100)/15,
    'take_profit_pct': 1/100,
    'quantity_discrete': 15,
    'averaging': (5/100),
    'cut_loss_usd': 15,
    'cut_loss_pct': (5/100),
    'halt_minute_before_reorder': 5, 
    'equity_risked_usd': 60, 
    'equity_risked_pct': (1/100)
    }
    ]