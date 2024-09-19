
from utilities.string_modification import (
    extract_integers_from_text)

from_sqlite_open= [{'order_id': '77661571195', 'label': 'hedgingSpot-open-1726498885066', 'amount': -10.0}, {'order_id': '77661569448', 'label': 'hedgingSpot-open-1726498884138', 'amount': -10.0}, {'order_id': '77661589759', 'label': 'hedgingSpot-open-1726498905866', 'amount': -10.0}, {'order_id': '77661589592', 'label': 'hedgingSpot-open-1726498905501', 'amount': -10.0}, {'order_id': '77661589116', 'label': 'hedgingSpot-open-1726498905278', 'amount': -10.0}, {'order_id': '77661588726', 'label': 'hedgingSpot-open-1726498905044', 'amount': -10.0}, {'order_id': '77661588527', 'label': 'hedgingSpot-open-1726498904669', 'amount': -10.0}, {'order_id': '77661640500', 'label': 'hedgingSpot-open-1726498948505', 'amount': -10.0}, {'order_id': '77661639978', 'label': 'hedgingSpot-open-1726498947643', 'amount': -10.0}, {'order_id': '77686608854', 'label': 'hedgingSpot-open-1726538930408', 'amount': -10.0}, {'order_id': '77686608442', 'label': 'hedgingSpot-open-1726538929449', 'amount': -10.0}, {'order_id': '77686789493', 'label': 'hedgingSpot-open-1726539346610', 'amount': -10.0}, {'order_id': '77686834266', 'label': 'hedgingSpot-open-1726539460964', 'amount': -10.0}, {'order_id': '77686999028', 'label': 'hedgingSpot-open-1726539753851', 'amount': -10.0}, {'order_id': '77686998837', 'label': 'hedgingSpot-open-1726539753224', 'amount': -10.0}]

integer_label= extract_integers_from_text(label)

trades_from_sqlite_open= [o for o in from_sqlite_open if integer_label in o["label"] and "open" in o["label"] ]