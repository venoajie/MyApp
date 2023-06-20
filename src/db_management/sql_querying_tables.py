# # -*- coding: utf-8 -*-


def querying_last_open_interest(
    last_tick: int, table: str = "ohlc1_eth_perp_json"
) -> str:

    return f"SELECT open_interest FROM {table} WHERE tick is {last_tick}"


def querying_open_interest(
    price: str = "close", table: str = "ohlc1_eth_perp_json"
) -> str:

    return f"""SELECT tick, JSON_EXTRACT (data, '$.volume') AS volume, JSON_EXTRACT (data, '$.{price}')  AS close, open_interest, \
        (open_interest - LAG (open_interest, 1, 0) OVER (ORDER BY tick)) as delta_oi FROM {table}"""


def querying_arithmetic_operator(
    item: str, operator: str = "MAX", table: str = "ohlc1_eth_perp_json"
) -> float:

    return f"SELECT {operator} ({item}) FROM {table}"


def querying_label_and_size(table) -> str:
    tab = f"SELECT label_main, amount_dir, price, timestamp, order_id FROM {table}"
    if "trade" in table:
        tab = f"SELECT label_main, amount_dir, price, timestamp, order_id, trade_seq FROM {table}"
    return tab
