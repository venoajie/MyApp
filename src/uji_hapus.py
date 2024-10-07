from dataclassy import dataclass, fields

@dataclass(unsafe_hash=True, slots=True)
class FutureSpreads():
    """ """
    ticker: list
    ask_price: float= fields

    def __post_init__(self):
        self.ask_price = (self.ticker ["best_ask_price"])*-1
        assert self.ask_price > 0
        print (f"self.ask_price {self.ask_price}")
        
combo_ticker = {'best_bid_amount': 255000.0, 'best_ask_amount': 59000.0, 'implied_bid': 82.0, 'implied_ask': 85.0, 'combo_state': 'active', 'best_bid_price': 59.5, 'best_ask_price': 60.0, 'mark_price': 86.09, 'max_price': 343.0, 'min_price': -171.0, 'settlement_price': 41.45, 'last_price': 60.0, 'instrument_name': 'BTC-FS-11OCT24_PERP', 'index_price': 63588.84, 'stats': {'volume_notional': 121880.0, 'volume_usd': 121880.0, 'volume': 0.0, 'price_change': 0.0, 'low': 48.0, 'high': 60.0}, 'state': 'open', 'type': 'change', 'timestamp': 1728262356179}

fut = FutureSpreads(combo_ticker)
