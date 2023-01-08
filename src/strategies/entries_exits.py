#!/usr/bin/env python
# -*- coding: utf-8 -*-

strategies = [
    {
    'strategy': 'supplyDemand15',
    'instrument': ['PERPETUAL'],
    'time_frame': 900,
    'take_profit': 15,
    'quantity_discrete': 15,
    'cut_loss': 15,
    'averaging': 15,
    'halt_time_before_reorder': 15,
    'risk': 1/100},
    {
    'strategy': 'hedgingSpot',
    'instrument': ['PERPETUAL'],
    'take_profit': 15,
    'quantity_discrete': 15,
    'averaging': 15,
    'cut_loss': 15,
    'halt_time_before_reorder': 15,
    'risk': 1/100},
    ]