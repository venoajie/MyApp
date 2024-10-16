# # -*- coding: utf-8 -*-

import sqlite3
from contextlib import contextmanager
import asyncio
import aiosqlite
from loguru import logger as log
import json
from utilities.string_modification import extract_currency_from_text
from transaction_management.deribit.telegram_bot import (
    telegram_bot_sendtext as telegram_bot,)

def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)


async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    return await telegram_bot(bot_message, purpose)


async def create_dataBase_sqlite(db_name: str = "databases/trading.sqlite3") -> None:
    """
    https://stackoverflow.com/questions/71729956/aiosqlite-result-object-has-no-attribue-execute
    """

    try:
        conn = await aiosqlite.connect(db_name)
        cur = await conn.cursor()
        await conn.commit()
        await conn.close()

    except Exception as error:
        print(error)


@contextmanager
async def db_ops(db_name: str = "databases/trading.sqlite3"):
    """
    # prepare sqlite initial connection + close
            Return and rtype: None
            #https://stackoverflow.com/questions/67436362/decorator-for-sqlite3/67436763#67436763
            # https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
            https://code-kamran.medium.com/python-convert-json-to-sqlite-d6fa8952a319
    """
    conn = await aiosqlite.connect(db_name, isolation_level=None)

    try:
        cur = await conn.cursor()
        yield cur

    except Exception as e:

        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(str(e), "failed_order")
        print(e)
        await conn.rollback()
        raise e

    else:
        await conn.commit()
        await conn.close()

async def insert_tables(table_name, params):
    """
    alternative insert format (safer):
    https://stackoverflow.com/questions/56910918/saving-json-data-to-sqlite-python

    """
    try:

        async with aiosqlite.connect(
            "databases/trading.sqlite3", isolation_level=None
        ) as db:

            # input was in list format. Insert them to db one by one
            # log.info(f"list {isinstance(params, list)} dict {isinstance(params, dict)}")
            log.error(f"isinstance(params, list) {isinstance(params, list)}")
            log.error(f"isinstance(params, dict) {isinstance(params, dict)}")
            log.error(f"isinstance(params, str) {isinstance(params, str)}")
            if isinstance(params, list):
                for param in params:

                    if "json" in table_name:

                        insert_table_json = f"""INSERT  OR IGNORE INTO {table_name} (data) VALUES (json ('{json.dumps(param)}'));"""
                        #log.error(f"insert_table_json {insert_table_json}")
                        #log.warning(f"{param}")

                        await db.execute(insert_table_json)

            # input is in dict format. Insert them to db directly
            if isinstance(params, dict) or isinstance(params, dict):

                if "json" in table_name:

                    insert_table_json = f"""INSERT OR IGNORE INTO {table_name} (data) VALUES (json ('{json.dumps(params)}'));"""

                    await db.execute(insert_table_json)

            log.error (f"insert_tables {insert_table_json} ")
    except Exception as error:
        log.error (f"insert_tables {table_name} {error}")

        await telegram_bot_sendtext("sqlite operation insert_tables", "failed_order")
        # await telegram_bot_sendtext(f"sqlite operation","failed_order")


async def querying_table(
    table: str = "mytrades",
    database: str = "databases/trading.sqlite3",
    filter: str = None,
    operator=None,
    filter_value=None,
) -> list:
    """
    Reference
    # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
    """

    from utilities import string_modification as str_mod

    NONE_DATA: None = [0, None, []]

    query_table = f"SELECT  * FROM {table} WHERE  {filter} {operator}?"

    filter_val = (f"{filter_value}",)

    if filter == None:
        query_table = f"SELECT  * FROM {table}"

    if "market_analytics" in table and "last" in table:
        query_table = f"SELECT  * FROM market_analytics_json ORDER BY id DESC LIMIT 1"

    combine_result = []

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            db = (
                db.execute(query_table)
                if filter == None
                else db.execute(query_table, filter_val)
            )

            async with db as cur:
                fetchall = await cur.fetchall()

                head = map(lambda attr: attr[0], cur.description)
                headers = list(head)

        for i in fetchall:
            combine_result.append(dict(zip(headers, i)))

    except Exception as error:
        log.error (f"querying_table  {table} {error}") 
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")

    return dict(
        all=[] if combine_result in NONE_DATA else (combine_result),
        list_data_only=(
            []
            if combine_result in NONE_DATA
            else str_mod.parsing_sqlite_json_output([o["data"] for o in combine_result])
        ),
    )


async def deleting_row(
    table: str = "mytrades",
    database: str = "databases/trading.sqlite3",
    filter: str = None,
    operator=None,
    filter_value=None,
) -> list:
    """ """

    query_table = f"DELETE  FROM {table} WHERE  {filter} {operator}?"
    log.debug (f"deleting_row {query_table}")

    filter_val = (f"{filter_value}",)

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            await db.execute(query_table, filter_val)

    except Exception as error:
        log.error (f"deleting_row {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")


async def querying_duplicated_transactions(
    label: str = "my_trades_all_json",
    group_by: str = "trade_id",
    database: str = "databases/trading.sqlite3",
) -> list:
    """ """

    #query_table = f"""SELECT CAST(SUBSTR((label),-13)as integer) AS label_int, count (*)  FROM {label} GROUP BY label_int HAVING COUNT (*) >1"""
    query_table = f"""SELECT {group_by} FROM {label} GROUP BY {group_by} HAVING count(*) >1"""
    combine_result = []

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            db = db.execute(query_table)

            async with db as cur:
                fetchall = await cur.fetchall()

                head = map(lambda attr: attr[0], cur.description)
                headers = list(head)

        for i in fetchall:
            combine_result.append(dict(zip(headers, i)))

    except Exception as error:
        log.error (f"querying_table {query_table} {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")

    return 0 if (combine_result == [] or combine_result == None) else (combine_result)


async def deleting_row(
    table: str = "mytrades",
    database: str = "databases/trading.sqlite3",
    filter: str = None,
    operator=None,
    filter_value=None,
) -> list:
    """ """

    query_table = f"DELETE  FROM {table} WHERE  {filter} {operator}?"
    query_table_filter_none = f"DELETE FROM {table}"

    filter_val = (f"{filter_value}",)

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            if filter == None:
                await db.execute(query_table_filter_none)
            else:
                await db.execute(query_table, filter_val)

    except Exception as error:
        log.error (f"deleting_row {query_table} {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")


async def add_additional_column(
    column_name,
    dataType,
    table: str = "ohlc1_eth_perp_json",
    database: str = "databases/trading.sqlite3",
) -> list:
    """ """

    try:
        query_table = f"ALTER TABLE {table} ADD {column_name} {dataType}"

        async with aiosqlite.connect(database, isolation_level=None) as db:
            db = await db.execute(query_table)

            async with db as cur:
                result = await cur.fetchone()

    except Exception as error:
        print(f"querying_table {query_table} {error}")
        await telegram_bot_sendtext("sqlite operation", "failed get_last_tick")

    try:
        return 0 if result == None else int(result[0])
    except:
        return None


def querying_additional_params(table: str = "supporting_items_json") -> str:

    return f"""SELECT JSON_EXTRACT (data, '$.label') AS label, JSON_EXTRACT (data, '$.take_profit')  AS take_profit FROM {table}"""


def querying_last_open_interest_tick(
    last_tick: int, table: str = "ohlc1_eth_perp_json"
) -> str:

    return f"SELECT open_interest FROM {table} WHERE tick is {last_tick}"


def querying_hedged_strategy(table: str = "my_trades_all_json") -> str:

    return f"SELECT * from {table} where not (label LIKE '%value1%' or label LIKE '%value2%' or label LIKE'%value3%');"


async def update_status_data(table: str, data_column: str, filter: str, filter_value: int, new_value, operator=None) -> None:
    """
    https://www.beekeeperstudio.io/blog/sqlite-json-with-text
    https://www.sqlitetutorial.net/sqlite-json-functions/sqlite-json_replace-function/
    https://stackoverflow.com/questions/75320010/update-json-data-in-sqlite3
    """
    
    if operator==None:
        where_clause= f"WHERE JSON_EXTRACT(data,'$.{filter}')  LIKE '%{filter_value}'"
     
    else:
        where_clause= f"WHERE  JSON_EXTRACT (data, '$.{filter}') {operator} {filter_value}"

    query = f"""UPDATE {table} SET data = JSON_REPLACE (data, '$.{data_column}', {new_value}) {where_clause};"""

    if "ohlc" in table:

        query = f"""UPDATE {table} SET {data_column} = JSON_REPLACE ('{json.dumps(new_value)}')   {where_clause};"""

        if data_column == "open_interest":

            query = f"""UPDATE {table} SET {data_column} = ({new_value})  {where_clause};"""

    #log.warning (f"query {query}")
    try:

        async with aiosqlite.connect(
            "databases/trading.sqlite3", isolation_level=None
        ) as db:
            await db.execute(query)

    except Exception as error:
        log.error (f" ERROR {error}")
        log.info (f"query update status data {query}")

        await telegram_bot_sendtext("sqlite operation insert_tables", "failed_order")
        # await telegram_bot_sendtext(f"sqlite operation","failed_order")


def querying_open_interest(
    price: float = "close", table: str = "ohlc1_eth_perp_json", limit: int = None
) -> str:

    all_data = f"""SELECT tick, JSON_EXTRACT (data, '$.volume') AS volume, JSON_EXTRACT (data, '$.{price}')  AS close, open_interest, \
        (open_interest - LAG (open_interest, 1, 0) OVER (ORDER BY tick)) as delta_oi FROM {table}"""
    return all_data if limit == None else f"""{all_data} limit {limit}"""


def querying_ohlc_price_vol(
    price: float = "close", table: str = "ohlc1_eth_perp_json", limit: int = None
) -> str:

    all_data = f"""SELECT  tick, JSON_EXTRACT (data, '$.volume') AS volume, JSON_EXTRACT (data, '$.{price}')  AS {price} FROM {table} ORDER BY tick DESC"""

    return all_data if limit == None else f"""{all_data} limit {limit}"""


def querying_hlc_vol(table: str = "ohlc1_eth_perp_json", limit: int = None) -> str:

    all_data = f"""SELECT  tick, JSON_EXTRACT (data, '$.volume') AS volume, JSON_EXTRACT (data, '$.high') AS high, JSON_EXTRACT (data, '$.low') AS low, JSON_EXTRACT (data, '$.close')  AS close FROM {table} ORDER BY tick DESC"""

    return all_data if limit == None else f"""{all_data} limit {limit}"""


def querying_ohlc_closed(
    price: float = "close", table: str = "ohlc1_eth_perp_json", limit: int = None
) -> str:

    all_data = f"""SELECT  JSON_EXTRACT (data, '$.{price}')  AS close FROM {table} ORDER BY tick DESC"""

    return all_data if limit == None else f"""{all_data} limit {limit}"""


def querying_arithmetic_operator(
    item: str, operator: str = "MAX", table: str = "ohlc1_eth_perp_json"
) -> float:

    return f"SELECT {operator} ({item}) FROM {table}"


def querying_label_and_size(table) -> str:
    tab = f"SELECT instrument_name, label, amount_dir as amount, price, timestamp, order_id FROM {table}"

    if "trade" in table:
        tab = f"SELECT instrument_name, label, amount_dir as amount, price, has_closed_label, timestamp, order_id, trade_id FROM {table}"
        
        if "closed" in table:
            tab = f"SELECT instrument_name, label, amount_dir as amount, order_id, trade_id FROM {table}"
    
    return tab


def querying_based_on_currency_or_instrument_and_strategy (table: str, 
                                                           currency_or_instrument, 
                                                           strategy: str="all", 
                                                           status: str="all",
                                                           columns: list="standard", 
                                                           limit: int= 0, 
                                                           order: str=None,
                                                           ordering: str = "DESC") -> str:
    
    """_summary_
    
    status: all, open, closed

    Returns:
        _type_: _description_
    """
    standard_columns= f"instrument_name, label, amount_dir as amount, timestamp, order_id"

    if "trade" in table or "order" in table:
        standard_columns= f"{standard_columns}, price"
        
        if "trade" in table:
        
            standard_columns= f"{standard_columns}, trade_id"
        
    if "transaction_log" in table:
        
        standard_columns= f"{standard_columns}, trade_id, price, type"
        
        table= f"transaction_log_{extract_currency_from_text(currency_or_instrument).lower()}_json"
        
        #log.error (f"table transaction_log {table}")
        
    if columns != "standard":
        
        if "data" in columns:
            standard_columns= (','.join(str(f"""{i}{("_dir as amount") if i=="amount" else ""}""") for i in columns))
                
        else:
            standard_columns= (','.join(str(f"""{i}{("_dir as amount") if i=="amount" else ""}""") for i in columns))
        
    where_clause= f"WHERE (instrument_name LIKE '%{currency_or_instrument}%')"

    if strategy != "all":
        where_clause= f"WHERE (instrument_name LIKE '%{currency_or_instrument}%' AND label LIKE '%{strategy}%')"
    
    if status != "all":
        where_clause= f"WHERE (instrument_name LIKE '%{currency_or_instrument}%' AND label LIKE '%{strategy}%' AND label LIKE '%{status}%')"
    
    tab = f"SELECT {standard_columns} FROM {table} {where_clause}"
    
    if order is not None:
            
            #tab = f"SELECT instrument_name, label_main as label, amount_dir as amount, order_id, trade_seq FROM {table} {where_clause} ORDER BY {order}"
            tab = f"SELECT {standard_columns} FROM {table} {where_clause} ORDER BY {order} {ordering} "
    
    if limit > 0:
        
        tab= f"{tab} LIMIT {limit}"
    
    #log.error (f"table {tab}")
    return tab

def querying_closed_transactions(
    limit: int = 20, order: str = "id", table: str = "my_trades_closed_json"
) -> str:
    return f"SELECT * FROM {table} ORDER BY {order} DESC LIMIT {limit}"


async def executing_closed_transactions(
    limit: int = 20, order: str = "id", table: str = "my_trades_closed_json"
) -> dict:
    """
    Provide execution template for querying summary of trading results from sqlite.
    Consist of transaction label, size, and price only.
    """

    # get query
    query = querying_closed_transactions(limit, order, table)
    # print(f"querying_closed_transactions {query}")

    # execute query
    result = await executing_query_with_return(query)

    # define none from queries result. If the result=None, return []
    NONE_DATA: None = [0, None, []]

    return [] if result in NONE_DATA else (result)


async def executing_query_based_on_currency_or_instrument_and_strategy(table: str, 
                                                           currency_or_instrument, 
                                                           strategy: str="all", 
                                                           status: str="all",
                                                           columns: list="standard", 
                                                           limit: int= 0, 
                                                           order: str="id") -> dict:
    """
    Provide execution template for querying summary of trading results from sqlite.
    Consist of transaction label, size, and price only.
    """

    # get query
    query = querying_based_on_currency_or_instrument_and_strategy (table, currency_or_instrument, strategy, status, columns, limit, order)
    
    # execute query
    result = await executing_query_with_return(query)
    
    #log.critical (f"table {table} filter {filter}")
    #log.info (f"result {result}")

    # define none from queries result. If the result=None, return []
    NONE_DATA: None = [0, None, []]
    
    #log.error (f"table {query}")
    #log.warning (f"result {result}")

    return [] if result in NONE_DATA else (result)

async def executing_query_with_return(
    query_table,
    filter: str = None,
    filter_value=None,
    database: str = "databases/trading.sqlite3",
) -> list:
    """
    Reference
    # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3

    Return type: 'list'/'dataframe'

    """

    filter_val = (f"{filter_value}",)

    combine_result = []

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            db = (
                db.execute(query_table)
                if filter == None
                else db.execute(query_table, filter_val)
            )

            async with db as cur:
                fetchall = await cur.fetchall()

                head = map(lambda attr: attr[0], cur.description)
                headers = list(head)

        for i in fetchall:
            combine_result.append(dict(zip(headers, i)))

    except Exception as error:
        #import traceback
        log.error (f"querying_table {query_table} {error}")
        #traceback.format_exc()
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")

    return 0 if (combine_result == [] or combine_result == None) else (combine_result)


async def executing_general_query(
    query_table,
    table: str = "mytrades",
    database: str = "databases/trading.sqlite3",
    filter: str = None,
    operator=None,
    filter_value=None,
) -> list:
    """
    Reference
    # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
    """

    filter_val = (f"{filter_value}",)

    if filter == None:
        query_table = f"SELECT  * FROM {table}"

    combine_result = []

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            db = (
                db.execute(query_table)
                if filter == None
                else db.execute(query_table, filter_val)
            )

            async with db as cur:
                fetchall = await cur.fetchall()

                head = map(lambda attr: attr[0], cur.description)
                headers = list(head)

        for i in fetchall:
            combine_result.append(dict(zip(headers, i)))

    except Exception as error:
        log.error (f"querying_table {query_table} {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")

    return 0 if (combine_result == [] or combine_result == None) else (combine_result)


def query_pd(table_name: str, field: str = None):
    """
    # fetch tickers from sqlite3 by pandas and transform them to dict
    # https://medium.com/@sayahfares19/making-pandas-fly-6-pandas-best-practices-to-save-memory-energy-8d09e9d52488
    # https://pythonspeed.com/articles/pandas-sql-chunking/
    """
    import pandas as pd

    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect("databases/trading.sqlite3")
    query_table = f"SELECT *  FROM {table_name}"

    if field != None:
        query_table = f"SELECT {field}  FROM {table_name}"

    # fetch all
    result = pd.read_sql_query(query_table, con)

    # transform dataframe to dict
    result = result.to_dict("records")

    result_cleaned = [o["data"] for o in result]

    # close connection sqlite
    con.close()

    return result_cleaned


async def back_up_db_sqlite():
    import sqlite3
    from datetime import datetime

    TIMESTAMP = datetime.now().strftime("%Y%m%d-%H-%M-%S")


    src = sqlite3.connect("databases/trading.sqlite3")
    dst = sqlite3.connect(f"databases/trdg-{TIMESTAMP}.bak")
    with dst:
        src.backup(dst)
    dst.close()
    src.close()
