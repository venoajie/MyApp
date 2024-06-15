# -*- coding: utf-8 -*-

# installed
from loguru import logger as log

# user defined formula
from utilities import (
    system_tools,
)
from db_management import sqlite_management

def catch_error(error, idle: int = None) -> list:
    """ """
    system_tools.catch_error_message(error, idle)


def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)


async def manage_orders (orders: dict) -> None:

    for order in orders:

        #! ##############################################################################

        open_orders_sqlite = await sqlite_management.executing_label_and_size_query(
            "orders_all_json"
        )
        len_open_orders_sqlite_list_data = len([o for o in open_orders_sqlite])

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
                order["order_id"]
                if order_state != "triggered"
                else ["stop_order_id'"]
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
                where_filter = f"label_main"

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
