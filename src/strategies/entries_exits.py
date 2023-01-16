#!/usr/bin/env python
# -*- coding: utf-8 -*-

strategies = [
    {
    'strategy': 'supplyDemandShort15',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'side': 'sell',
    'entry_price': 1544,
    'take_profit_usd': 1543.5,
    'take_profit_pct': 1/100,
    'quantity_discrete': 15,
    'cut_loss_usd': 1544.5,
    'cut_loss_pct': (1/100)/2,
    'averaging': 15,
    'halt_minute_before_reorder': 60, 
    'equity_risked_usd': 60, 
    'equity_risked_pct': 1/100
    },
    
    {
    'strategy': 'supplyDemandLong15',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'side': 'buy',
    'entry_price': 1542,
    'take_profit_usd': 1542.5,
    'take_profit_pct': 1/100,
    'quantity_discrete': 900,
    'cut_loss_usd': 1543.5,
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
    'averaging': (1/100)/2,
    'cut_loss_usd': 15,
    'cut_loss_pct': (1/100)/2,
    'halt_minute_before_reorder': 1/10, 
    'equity_risked_usd': 60, 
    'equity_risked_pct': (1/100)/10
    }
    ]