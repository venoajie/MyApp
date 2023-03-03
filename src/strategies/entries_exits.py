# -*- coding: utf-8 -*-
equity_risked_pct_default =  1/100/4

strategies = [
    {
    'strategy': 'supplyDemandShort60',
    'instrument': ['PERPETUAL'],
    'time_frame': 3600,
    'side': 'sell',
    'entry_price': 1675,
    'take_profit_usd': 1640,
    'take_profit_pct': 1/100,
    'quantity_discrete': 15,
    'cut_loss_usd': 1720,
    'cut_loss_pct': (1/100)/2,
    'averaging': 15,
    'halt_minute_before_reorder': 60, 
    'equity_risked_usd': 60, 
    'equity_risked_pct': equity_risked_pct_default
    },
    
    {
    'strategy': 'supplyDemandLong60',
    'instrument': ['PERPETUAL'],
    'time_frame': 3600,
    'side': 'buy',
    'entry_price': 1635,
    'take_profit_usd': 1670,
    'take_profit_pct': 1/100,
    'quantity_discrete': 15,
    'cut_loss_usd': 1570,
    'cut_loss_pct': (1/100)/2,
    'averaging': 15,
    'halt_minute_before_reorder': 60, 
    'equity_risked_usd': 60, 
    'equity_risked_pct': equity_risked_pct_default
    },
    
    {
    'strategy': 'supplyDemandLong60A',
    'instrument': ['PERPETUAL'],
    'time_frame': 3600,
    'side': 'buy',
    'entry_price': 1640,
    'take_profit_usd': 1670,
    'take_profit_pct': 1/100,
    'quantity_discrete': 15,
    'cut_loss_usd': 1570,
    'cut_loss_pct': (1/100)/2,
    'averaging': 15,
    'halt_minute_before_reorder': 60, 
    'equity_risked_usd': 60, 
    'equity_risked_pct': equity_risked_pct_default
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