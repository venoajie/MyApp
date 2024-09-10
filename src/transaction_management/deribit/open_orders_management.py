# -*- coding: utf-8 -*-

# installed
from loguru import logger as log

# user defined formula
from db_management import sqlite_management


def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)


async def manage_orders(order: dict) -> None:

    log.error(f"{order}")

    #! ##############################################################################

    open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
        "orders_all_json"
    )

    if "oto_order_ids" in order:
        # get the order state
        oto_order_ids = order["oto_order_ids"]
        log.error(f"oto_order_ids {oto_order_ids}")

    if "is_primary_otoco" in order:
        # get the order state
        is_primary_otoco = order["is_primary_otoco'"]
        log.error(f"is_primary_otoco {is_primary_otoco}")

    if "is_secondary_oto" in order:
        # get the order state
        is_secondary_oto = order["is_secondary_oto'"]
        log.error(f"is_secondary_oto {is_secondary_oto}")

    if "oco_ref" in order:
        # get the order state
        oco_ref = order["oco_ref'"]
        log.error(f"oco_ref {oco_ref}")

    if "oto_order_ids" in order:
        # get the order state
        oto_order_ids = order["oto_order_ids"]
        log.error(f"oto_order_ids {oto_order_ids}")

    if "trade_seq" not in order:
        # get the order state
        order_state = order["order_state"]

    if "trade_seq" in order:

        # get the order state
        order_state = order["state"]

    log.error(f"ORDER STATE {order_state}")

    if (
        order_state == "cancelled"
        or order_state == "filled"
        or order_state == "triggered"
    ):

        order_id = (
            order["order_id"] if order_state != "triggered" else ["stop_order_id'"]
        )

        # open_orders_sqlite =  await syn.querying_all('orders_all_json')
        open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
            "orders_all_json"
        )
        # open_orders_sqlite_list_data =  open_orders_sqlite['list_data_only']

        is_order_id_in_active_orders = [
            o for o in open_orders_sqlite if o["order_id"] == order_id
        ]

        where_filter = f"order_id"
        if is_order_id_in_active_orders == []:
            order_id = order["label"]
            where_filter = f"label"

        log.critical(f" deleting {order_id}")
        await sqlite_management.deleting_row(
            "orders_all_json",
            "databases/trading.sqlite3",
            where_filter,
            "=",
            order_id,
        )

    if (
        order_state == "open"
        or order_state == "untriggered"
        or order_state == "triggered"
    ):

        await sqlite_management.insert_tables("orders_all_json", order)
