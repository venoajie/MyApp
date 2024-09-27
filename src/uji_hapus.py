trading={
  "positions": [
    {
      "size_currency": -0.04591948,
      "realized_funding": 0.000006,
      "total_profit_loss": -0.000957063,
      "realized_profit_loss": 0.000010673,
      "floating_profit_loss": 0.000140281,
      "leverage": 50,
      "average_price": 2559.92,
      "delta": -0.04591948,
      "interest_value": 1.598993597488471,
      "mark_price": 2613.27,
      "settlement_price": 2622.37,
      "instrument_name": "ETH-PERPETUAL",
      "initial_margin": 0.000918398,
      "maintenance_margin": 0.000459203,
      "index_price": 2612.25,
      "direction": "sell",
      "kind": "future",
      "size": -120
    }
  ],
  "trades": [],
  "instrument_name": "ETH-PERPETUAL",
  "orders": [
    {
      "is_liquidation": False,
      "risk_reducing": False,
      "order_type": "limit",
      "creation_timestamp": 1727329393532,
      "order_state": "open",
      "reject_post_only": False,
      "contracts": 1,
      "average_price": 0,
      "reduce_only": False,
      "last_update_timestamp": 1727329393532,
      "filled_amount": 0,
      "post_only": True,
      "replaced": False,
      "mmp": False,
      "order_id": "ETH-49570653817",
      "web": True,
      "api": False,
      "instrument_name": "ETH-PERPETUAL",
      "max_show": 1,
      "time_in_force": "good_til_cancelled",
      "direction": "sell",
      "amount": 1,
      "price": 2800,
      "label": ""
    }
  ]
}

label = trading["orders"][0]["label"] 
orders = trading["orders"] 
trades = trading["trades"]
positions = trading["positions"]

if label:
  print(f"""AAAAAAAAAAAA {(orders)}""")
if trades:
  print(f"""BBBBBBBBBBBBBBB {(trades)}""")
#print(f"""{(positions)}""")