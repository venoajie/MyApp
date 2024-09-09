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
    """ """
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

    if "portfolio_json" in table or "account_summary_json" in table or "market_analytics_json" in table or "supporting_items_json" in table:
        query = f"""
                        CREATE 
                        TABLE IF NOT EXISTS 
                            {table} 
                            (id INTEGER PRIMARY KEY, data TEXT, time_stamp  INTEGER)
                        """
    return query


def texting_virtual_table(table: str, item: str, item_data_type: str) -> str:
    """ """
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

            if "trades"  in table or "orders"  in table:

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
                create_table_alter_instrument_name_strategy = texting_virtual_table(
                    table, "instrument_name", "TEXT"
                )
                
                create_table_alter_label_strategy = texting_virtual_table(
                    table, "label", "TEXT"
                )

                create_table_alter_label_strategy_order = texting_virtual_table(
                    table, "timestamp", "INTEGER"
                )

                create_table_alter_order_id = texting_virtual_table(
                    table, "order_id", "TEXT"
                )
                
                create_table_alter_has_closed_label = texting_virtual_table(
                    table, "has_closed_label", "INTEGER"
                )

                create_table_alter_trade_id = texting_virtual_table(
                    table, "trade_id", "TEXT"
                )

                create_table_alter_timestamp = texting_virtual_table(
                    table, "timestamp", "INTEGER"
                )

                create_table_alter_price = texting_virtual_table(table, "price", "REAL")


                print(f"create virtual columns {create_table_alter_instrument_name_strategy}")
                await cur.execute(f"{create_table_alter_instrument_name_strategy}")
                
                print(f"create virtual columns {create_table_alter_label_strategy}")
                await cur.execute(f"{create_table_alter_label_strategy}")
                
                if "orders_all" in table:

                    await cur.execute(f"{create_table_alter_label_strategy_order}")
                    print(
                        f"create virtual columns {create_table_alter_label_strategy_order}"
                    )

                if  "my_trades" in table:

                    await cur.execute(f"{create_table_alter_trade_id}")
                    print(f"create virtual columns {create_table_alter_trade_id}")
                    
                    await cur.execute(f"{create_table_alter_timestamp}")
                    print(f"create virtual columns {create_table_alter_timestamp}")
                    
                    if  "closed" not in table:
                        await cur.execute(f"{create_table_alter_has_closed_label}")
                        print(f"create virtual columns {create_table_alter_has_closed_label}")
                    

                print(f"create virtual columns {create_table_alter_order_id}")
                await cur.execute(f"{create_table_alter_order_id}")
                
                print(f"create virtual columns {create_table_alter_sum_pos}")
                await cur.execute(f"{create_table_alter_sum_pos}")
                
                print(f"create virtual columns {create_table_alter_price}")
                await cur.execute(f"{create_table_alter_price}")

                create_index = f"""CREATE INDEX order_id ON  {table} (order_id);"""

                if "my_trades" in table:

                    create_index = f"""CREATE INDEX trade_id ON  {table} (trade_id);"""
                    print(f"create_index trd_id {create_index}")

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


async def querying_tables_item_data(table_name: str):
    """ """
    import ast

    # Read sqlite query results into a pandas DataFrame

    query_table = f"SELECT data  FROM {table_name}"

    # fetch all
    result = await executing_query_with_return(query_table)

    return [] if result == [] else [ast.literal_eval(str(i["data"])) for i in result]
