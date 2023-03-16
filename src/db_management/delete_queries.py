# -*- coding: utf-8 -*-

from db_management import sqlite_management
from loguru import logger as log


def telegram_bot_sendtext(bot_message, purpose) -> None:
    from utils import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)


def deleting_expired_instrument(instrument, table: str = "strategy_entries") -> list:
    """ """
    query_table = "DELETE FROM strategy_entries WHERE instrument=?"
    # query_table = f'SELECT * FROM {table}'
    # query_table = f'DELETE {table} WHERE instrument =?'
    log.info(query_table)

    try:
        with sqlite_management.db_ops() as cur:
            cur.execute(query_table, (instrument,))

    except Exception as error:
        from utils import formula

        info = f" deleting expired instrument {instrument} "
        telegram_bot_sendtext(info, "general_error")
        formula.log_error(
            "deleting instrument",
            f"deleting expired instrument {instrument}",
            error,
            30,
        )


def deleting_items_based_on_strategyId(
    strategyId, table: str = "strategy_entries"
) -> list:
    """ """
    query_table = "DELETE FROM strategy_entries WHERE strategyId=?"

    try:
        with sqlite_management.db_ops() as cur:
            cur.execute(query_table, (strategyId,))

    except Exception as error:
        from utils import formula

        info = f" deleting expired id {strategyId} "
        telegram_bot_sendtext(info, "general_error")
        formula.log_error(
            "deleting instrument", f"deleting expired id {strategyId}", error, 30
        )
