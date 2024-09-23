transaction= {"liquidity":"M","risk_reducing":False,"order_type":"limit","combo_trade_id":"317811582",
              "trade_id":"317811588","fee_currency":"BTC","contracts":1.0,"self_trade":False,"combo_id":"BTC-FS-20SEP24_PERP",
              "reduce_only":False,"post_only":False,"mmp":False,"tick_direction":3,"fee":-2e-08,"matching_id":None,"order_id":"77715549856",
              "mark_price":60168.39,"api":False,"trade_seq":41810,"instrument_name":"BTC-20SEP24","profit_loss":0.0,"index_price":60126.61,
              "direction":"sell","amount":10.0,"price":60163.5,"state":"filled","timestamp":1726583974512,
              "label":"futureSpread-open-1726583974512","take_profit":0,"has_closed_label":False}

has_closed_label= True

transaction.update({"has_closed_label":has_closed_label})
print (transaction)