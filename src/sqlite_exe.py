# # -*- coding: utf-8 -*-
import asyncio
# user defined formula
from db_management import sqlite_management

def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)
    
async  def main() -> list:
    """ """

    await sqlite_management.create_dataBase_sqlite('databases/trading.sqlite3')

    await sqlite_management.create_tables()
    query=await sqlite_management.querying_table('myTradesOpen',  '=', 'filled')
    print (query)
        
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())

    except (KeyboardInterrupt, SystemExit):
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 10)

