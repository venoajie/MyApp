# # -*- coding: utf-8 -*-

import sqlite3
from contextlib import contextmanager
import asyncio
import aiosqlite
from loguru import logger as log
import json


def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)


async def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    import deribit_get

    return await deribit_get.telegram_bot_sendtext(bot_message, purpose)


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
async def db_ops(db_name: str = "databases/trading.sqlite3") -> None:
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


def create_table_json(table) -> str:

    """
    """
    query = f"""
                CREATE 
                TABLE IF NOT EXISTS 
                    {table} 
                    (id INTEGER PRIMARY KEY, data TEXT)
            """

    if "ohlc1" in table:
        query = f"""
                        CREATE 
                        TABLE IF NOT EXISTS 
                            {table} 
                            (id INTEGER PRIMARY KEY, data TEXT, open_interest REAL)
                        """
    return query


def create_virtual_table(table: str, item: str, item_data_type: str) -> str:

    """
    """
    query = f""" 
            ALTER 
            TABLE 
                {table} 
            ADD COLUMN 
                {item} {item_data_type}  
            GENERATED ALWAYS AS 
            (
            (JSON_EXTRACT (data, '$.{item}'))
            ) 
            VIRTUAL;
            
            """

    return query


async def create_tables(type: str = None):

    """
    type: json/None
    
    Naming conventions to ensure portability:
        - all in lower case (except myTrades to distingush my own trade (private) and exchanges trade (public))
        - use underscores
        - when possible, name is started with api endpoint
        - examples:
            - db in pickle: eth-myTrades-open
            - sqlite: myTrades_open -> eth will be resolved through queries

    https://antonz.org/json-virtual-columns/ 
    https://www.beekeeperstudio.io/blog/sqlite-json-with-text
    """
    async with aiosqlite.connect(
        "databases/trading.sqlite3", isolation_level=None
    ) as cur:

        tables = [
            "my_trades_open",
            "my_trades_closed",
            "my_trades_all",
            "orders_open",
            "orders_all",
            "orders_closed",
            "orders_untrig",
            "my_trades_all_json",
            "my_trades_closed_json",
            "orders_all_json",
            "ohlc1_eth_perp_json",
            "ohlc3_eth_perp_json",
            "ohlc5_eth_perp_json",
            "ohlc15_eth_perp_json",
            "ohlc30_eth_perp_json",
            "ohlc1H_eth_perp_json",
            "positions_json",
            "portfolio_json",
        ]

        try:
            for table in tables:
                print(table)

                # await cur.execute(f"DROP TABLE IF EXISTS {table}")

                create_table = create_table_json(table)

                if "myTrades" in table or "my_trades" in table:

                    if "json" in table:
                        create_table = create_table_json(table)

                    else:
                        create_table = f"""CREATE 
                                            TABLE IF NOT EXISTS 
                                                {table} 
                                                (instrument_name TEXT,
                                                label TEXT,
                                                direction TEXT, 
                                                amount REAL, 
                                                price REAL, 
                                                state TEXT, 
                                                order_type TEXT,
                                                timestamp INTEGER,
                                                trade_seq INTEGER,
                                                trade_id TEXT, 
                                                tick_direction INTEGER, 
                                                order_id TEXT, 
                                                api BOOLEAN NOT NULL CHECK (api IN (0, 1)),
                                                fee REAL)
                                        """

                if "orders" in table:
                    # log.debug ('json' in table)

                    if "json" in table:
                        create_table = create_table_json(table)

                    else:
                        create_table = f"CREATE TABLE IF NOT EXISTS {table} (instrument_name TEXT, \
                                                                    label TEXT, \
                                                                    direction TEXT, \
                                                                    amount REAL, \
                                                                    price REAL, \
                                                                    trigger_price REAL, \
                                                                    stop_price REAL, \
                                                                    order_state TEXT, \
                                                                    order_type TEXT, \
                                                                    last_update_timestamp INTEGER, \
                                                                    order_id TEXT, \
                                                                    is_liquidation BOOLEAN NOT NULL CHECK (is_liquidation IN (0, 1)), \
                                                                    api BOOLEAN NOT NULL CHECK (api IN (0, 1)))"

                await cur.execute(f"{create_table}")

                if "json" in table and "ohlc" not in table:

                    create_table_alter_sum_pos = f""" 
                                                    ALTER 
                                                    TABLE 
                                                        {table} 
                                                    ADD COLUMN 
                                                        amount_dir REAL  
                                                    GENERATED ALWAYS AS 
                                                    (
                                                    (CASE WHEN 
                                                    JSON_EXTRACT (data, '$.direction')='sell'
                                                    THEN 
                                                    JSON_EXTRACT (data, '$.amount')  * -1
                                                    ELSE 
                                                    JSON_EXTRACT (data, '$.amount')  
                                                    END)
                                                    ) 
                                                    VIRTUAL;
                                                    
                                                    """
                    create_table_alter_label_strategy = f""" 
                                                    ALTER 
                                                    TABLE 
                                                        {table} 
                                                    ADD COLUMN 
                                                        label_main TEXT  
                                                    GENERATED ALWAYS AS 
                                                    (
                                                    (JSON_EXTRACT (data, '$.label'))
                                                    ) 
                                                    VIRTUAL;
                                                    
                                                    """
                    create_table_alter_label_strategy_order = f""" 
                                                    ALTER 
                                                    TABLE 
                                                        {table} 
                                                    ADD COLUMN 
                                                        timestamp INTEGER  
                                                    GENERATED ALWAYS AS 
                                                    (
                                                    (JSON_EXTRACT (data, '$.last_update_timestamp'))
                                                    ) 
                                                    VIRTUAL;
                                                    
                                                    """

                    create_table_alter_order_id = create_virtual_table(
                        table, "order_id", "TEXT"
                    )

                    create_table_alter_trade_seq = create_virtual_table(
                        table, "trade_seq", "INTEGER"
                    )

                    create_table_alter_timestamp = create_virtual_table(
                        table, "timestamp", "INTEGER"
                    )

                    create_table_alter_price = create_virtual_table(
                        table, "price", "REAL"
                    )

                    if "orders_all" in table:

                        await cur.execute(f"{create_table_alter_label_strategy_order}")
                        print(
                            f"create virtual columns {create_table_alter_label_strategy_order}"
                        )

                    if "myTrades" in table or "my_trades" in table:

                        await cur.execute(f"{create_table_alter_trade_seq}")
                        print(f"create virtual columns {create_table_alter_trade_seq}")
                        await cur.execute(f"{create_table_alter_timestamp}")
                        print(f"create virtual columns {create_table_alter_timestamp}")

                    print(f"create virtual columns {create_table_alter_order_id}")
                    await cur.execute(f"{create_table_alter_order_id}")
                    print(f"create virtual columns {create_table_alter_label_strategy}")
                    await cur.execute(f"{create_table_alter_label_strategy}")
                    print(f"create virtual columns {create_table_alter_sum_pos}")
                    await cur.execute(f"{create_table_alter_sum_pos}")
                    print(f"create virtual columns {create_table_alter_price}")
                    await cur.execute(f"{create_table_alter_price}")

                    create_index = f"""CREATE INDEX order_id ON  {table} (order_id);"""

                    if "myTrades" in table or "my_trades" in table:

                        create_index = f"""CREATE INDEX id ON  {table} (trade_seq);"""
                        print(f"create_index myTrades {create_index}")

                    else:
                        await cur.execute(f"{create_index}")

                if "ohlc" in table:

                    create_table_alter_tick = create_virtual_table(
                        table, "tick", "INTEGER"
                    )

                    create_index = f"""CREATE INDEX tick ON  {table} (tick);"""
                    await cur.execute(f"{create_table_alter_tick}")
                    await cur.execute(f"{create_index}")

        except Exception as error:
            print(f"create_tables {error}")
            await telegram_bot_sendtext(
                "sqlite operation-failed_create_table", "failed_order"
            )
            await telegram_bot_sendtext(
                f"sqlite operation-create_table", "failed_order"
            )


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
            # log.error(f"params {params}")
            if isinstance(params, list):
                for param in params:

                    if "json" in table_name:

                        insert_table_json = f"""INSERT INTO {table_name} (data) VALUES (json ('{json.dumps(param)}'));"""

                        await db.execute(insert_table_json)

            # input is in dict format. Insert them to db directly
            if isinstance(params, dict):

                if "json" in table_name:

                    insert_table_json = f"""INSERT INTO {table_name} (data) VALUES (json ('{json.dumps(params)}'));"""

                    await db.execute(insert_table_json)

    except Exception as error:
        print(f"insert_tables {table_name} {error}")

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
        print(f"querying_table {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")

    return dict(
        all=[] if combine_result in NONE_DATA else (combine_result),
        list_data_only=[]
        if combine_result in NONE_DATA
        else str_mod.parsing_sqlite_json_output([o["data"] for o in combine_result]),
    )


async def deleting_row(
    table: str = "mytrades",
    database: str = "databases/trading.sqlite3",
    filter: str = None,
    operator=None,
    filter_value=None,
) -> list:

    """
    """

    query_table = f"DELETE  FROM {table} WHERE  {filter} {operator}?"

    filter_val = (f"{filter_value}",)

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            await db.execute(query_table, filter_val)

    except Exception as error:
        print(f"deleting_row {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")


async def querying_completed_transactions(
    database: str = "databases/trading.sqlite3",
) -> list:

    """
    """

    query_table = f"""SELECT  * FROM (select REPLACE(REPLACE (label_main,'closed-',''), 'open-','') as label, sum(amount_dir) as amount_net FROM my_trades_all_json group by result)"""

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
        print(f"querying_table {error}")
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

    """
    """

    query_table = f"DELETE  FROM {table} WHERE  {filter} {operator}?"

    filter_val = (f"{filter_value}",)

    try:
        async with aiosqlite.connect(database, isolation_level=None) as db:
            await db.execute(query_table, filter_val)

    except Exception as error:
        print(f"deleting_row {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")


async def add_additional_column(
    column_name,
    dataType,
    table: str = "ohlc1_eth_perp_json",
    database: str = "databases/trading.sqlite3",
) -> list:

    """
    """

    try:
        query_table = f"ALTER TABLE {table} ADD {column_name} {dataType}"

        async with aiosqlite.connect(database, isolation_level=None) as db:
            db = await db.execute(query_table)

            async with db as cur:
                result = await cur.fetchone()

    except Exception as error:
        print(f"querying_table {error}")
        await telegram_bot_sendtext("sqlite operation", "failed get_last_tick")

    try:
        return 0 if result == None else int(result[0])
    except:
        return None


async def replace_row(
    new_value: dict,
    column_name: str = "data",
    table: str = "ohlc1_eth_perp_json",
    database: str = "databases/trading.sqlite3",
    filter: str = None,
    operator=None,
    filter_value=None,
) -> list:

    """
    """

    try:

        query_table = f"""UPDATE {table} SET {column_name} = json_replace('{json.dumps(new_value)}')  WHERE  JSON_EXTRACT (data, '$.{filter}') {operator} 
        
        {filter_value};"""

        if column_name == "open_interest":

            query_table = f"""UPDATE {table} SET {column_name} = ({new_value})  WHERE  JSON_EXTRACT (data, '$.{filter}') {operator} {filter_value};"""
            # print (f'query_table {query_table}')

        async with aiosqlite.connect(database, isolation_level=None) as db:
            await db.execute(query_table)
    # CREATE INDEX tick_index ON  ohlc1_eth_perp_json (tick);
    except Exception as error:
        print(f"replace_row {error}")
        await telegram_bot_sendtext("sqlite failed replace_row", "failed_order")


def querying_last_open_interest(
    last_tick: int, table: str = "ohlc1_eth_perp_json"
) -> str:

    return f"SELECT open_interest FROM {table} WHERE tick is {last_tick}"


def querying_hedged_strategy(table: str = "my_trades_all_json") -> str:

    return f"SELECT * from {table} where not (label_main LIKE '%value1%' or label_main LIKE '%value2%' or label_main LIKE'%value3%');"


def querying_open_interest(
    price: float = "close", table: str = "ohlc1_eth_perp_json"
) -> str:

    return f"""SELECT tick, JSON_EXTRACT (data, '$.volume') AS volume, JSON_EXTRACT (data, '$.{price}')  AS close, open_interest, \
        (open_interest - LAG (open_interest, 1, 0) OVER (ORDER BY tick)) as delta_oi FROM {table}"""


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
    tab = f"SELECT label_main, amount_dir, price, timestamp, order_id FROM {table}"
    if "trade" in table:
        tab = f"SELECT label_main, amount_dir, price, timestamp, order_id, trade_seq FROM {table}"
    return tab


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
        print(f"querying_table {error}")
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
        print(f"querying_table {error}")
        await telegram_bot_sendtext("sqlite operation", "failed_order")
        await telegram_bot_sendtext(f"sqlite operation-{query_table}", "failed_order")

    return 0 if (combine_result == [] or combine_result == None) else (combine_result)


async def executing_label_and_size_query(table) -> dict:
    """
    Provide execution template for querying summary of trading results from sqlite.
    Consist of transaction label, size, and price only.
    """

    # get query
    query = querying_label_and_size(table)

    # execute query
    result = await executing_query_with_return(query)

    # define none from queries result. If the result=None, return []
    NONE_DATA: None = [0, None, []]

    return [] if result in NONE_DATA else (result)


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
