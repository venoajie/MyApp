#!/usr/bin/env python
# -*- coding: utf-8 -*-

strategies = [
    {
    'strategy': 'supplyDemandShort15',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'side': 'sell',
    'entry_price': 1544,
    'take_profit': 1543.5,
    'quantity_discrete': 15,
    'cut_loss': 1544.5,
    'averaging': 15,
    'halt_minute_before_reorder': 60, 
    'equity_risked': 1/100
    },
    {
    'strategy': 'supplyDemandLong15',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'side': 'buy',
    'entry_price': 1542,
    'take_profit': 1542.5,
    'quantity_discrete': 900,
    'cut_loss': 1543.5,
    'averaging': 15,
    'halt_minute_before_reorder': 60, 
    'equity_risked': 1/100
    },
    
    {
    'strategy': 'hedgingSpot',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'side': 900,
    'entry_price': 1000,
    'take_profit': (1/100)/15,
    'quantity_discrete': 15,
    'averaging': (1/100)/2,
    'cut_loss': 15,
    'halt_minute_before_reorder': 1/10, 
    'equity_risked': (1/100)/10
    },
    ]