# # -*- coding: utf-8 -*-

"""
Provide table manipulation queries:
- create tables
- create index
- delete tables
"""


def create_db(db_name: str = "databases/trading", ext: str = "sqlite3") -> str:
    """
    db_name: folder location + file name
    """
    return f"""{db_name}.{ext}"""


def create_table_json(table) -> str:
    """
    default table for data saved in json format
    """
    # general query
    query = f"""
                CREATE 
                TABLE IF NOT EXISTS 
                    {table} 
                    (id INTEGER PRIMARY KEY, data TEXT)
            """

    # 1 minute time frame, + open interest
    if "ohlc1_" in table:
        query = f"""
                        CREATE 
                        TABLE IF NOT EXISTS 
                            {table} 
                            (id INTEGER PRIMARY KEY, data TEXT, open_interest REAL)
                        """
    return query


def create_virtual_table(table: str, item: str, item_data_type: str) -> str:
    """ """
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

