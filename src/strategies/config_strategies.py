# -*- coding: utf-8 -*-

"""
For strategy with many derivatives name (a/b/c):
    good strategy name: 1) 'supplyDemandShort60A'/'supplyDemandShort60B'/supplyDemandShort60C'
    bad strategy name: 'supplyDemandShort60'
    why? because in sorting process, supplyDemandShort60 means all strategy 
        contains 'supplyDemandShort60', not exclusively 'supplyDemandShort60'
"""

def paramaters_to_balancing_transactions() -> list:
    """ """

    return dict(max_transactions_downloaded_from_exchange=50,
                max_closed_transactions_downloaded_from_sqlite=20
                )


def max_rows(table) -> int:
    """ """
    if "market_analytics_json" in table:
        threshold= 10
    if "ohlc" in table:
        threshold= 10000
    if "supporting_items_json" in table:
        threshold= 200
    return threshold
