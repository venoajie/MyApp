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


async def create_dataBase_sqlite(
    db_name: str = "databases/trading", ext: str = "sqlite3"
) -> None:
    """
    https://stackoverflow.com/questions/71729956/aiosqlite-result-object-has-no-attribue-execute
    """
    from db_management import sql_manipulating_db_tables

    db = sql_manipulating_db_tables.create_db(db_name, ext)

    try:
        conn = await aiosqlite.connect(db)
        cur = await conn.cursor()
        await conn.commit()
        await conn.close()

    except Exception as error:
        print(f"failed create db {error}")


def texting_table_json(table) -> str:

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


def texting_virtual_table(table: str, item: str, item_data_type: str) -> str:

    """
    """
    item2 = "last_update_timestamp" if item == "timestamp" else item
    query = f""" 
            ALTER 
            TABLE 
                {table} 
            ADD COLUMN 
                {item} {item_data_type}  
            GENERATED ALWAYS AS 
            (
            (JSON_EXTRACT (data, '$.{item2}'))
            ) 
            VIRTUAL;
            
            """

    return query


async def create_tables_json_sqlite(table, type: str = None):

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

        try:
            print(table)

            # await cur.execute(f"DROP TABLE IF EXISTS {table}")

            create_table = texting_table_json(table)

            await cur.execute(f"{create_table}")

            if "ohlc" not in table:

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
                create_table_alter_label_strategy = texting_virtual_table(
                    table, "label_main", "TEXT"
                )

                create_table_alter_label_strategy_order = texting_virtual_table(
                    table, "timestamp", "INTEGER"
                )

                create_table_alter_order_id = texting_virtual_table(
                    table, "order_id", "TEXT"
                )

                create_table_alter_trade_seq = texting_virtual_table(
                    table, "trade_seq", "INTEGER"
                )

                create_table_alter_timestamp = texting_virtual_table(
                    table, "timestamp", "INTEGER"
                )

                create_table_alter_price = texting_virtual_table(table, "price", "REAL")

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

                create_table_alter_tick = texting_virtual_table(
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



async def query_data_pd(table_name: str):
    """
    # fetch tickers from sqlite3 by pandas and transform them to dict
    # https://medium.com/@sayahfares19/making-pandas-fly-6-pandas-best-practices-to-save-memory-energy-8d09e9d52488
    # https://pythonspeed.com/articles/pandas-sql-chunking/
    """
    import pandas as pd
    import ast
    from utilities import string_modification as str_mod

    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect("databases/trading.sqlite3")
    query_table = f"SELECT data  FROM {table_name}"

    # fetch all
    result = pd.read_sql_query(query_table, con)
    log.error(result)
    result = await executing_query_with_return(query_table)
    log.debug(result)
    result = [] if result ==[] else [ast.literal_eval(str(i['data'])) for i in result]

    log.warning(result)

    # transform dataframe to dict
    result = result.to_dict("records")
    
    # close connection sqlite
    con.close()

    return result