
data_from_db_trade_open= [{'trade_id': '319556178', 'label': 'hedgingSpot-closed-1726878643143'}, {'trade_id': '319556178', 'label': 'hedgingSpot-closed-1726878643143'}, {'trade_id': '319556178', 'label': 'hedgingSpot-closed-1726878643143'}, {'trade_id': '319556178', 'label': 'hedgingSpot-closed-1726878643143'}, {'trade_id': '319556178', 'label': 'hedgingSpot-closed-1726878643143'}, {'trade_id': '319556178', 'label': 'hedgingSpot-closed-1726878643143'}]
result_order_id= [o["trade_id"] for o in data_from_db_trade_open]
print (f"result_order_id {result_order_id}")