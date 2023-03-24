# # -*- coding: utf-8 -*-
import asyncio
import asyncio
import aioschedule as schedule
import time
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
    #query=await sqlite_management.querying_table('myTradesOpen', 'state', '=', 'filled')
    #print (query)
        

async def job(message='stuff', n=1):
    print("Asynchronous invocation (%s) of I'm working on:" % n, message)
    asyncio.sleep(1)
    
if __name__ == "__main__":
    
        
    for i in range(1,3):
        schedule.every(1).seconds.do(job, n=i)
    schedule.every(5).to(10).days.do(job)
    schedule.every().hour.do(job, message='things')
    schedule.every().day.at("10:30").do(job)

    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(schedule.run_pending())
        time.sleep(0.1)
        
    try:
        asyncio.get_event_loop().run_until_complete(main())

    except (KeyboardInterrupt, SystemExit):
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 10)

