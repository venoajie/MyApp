from db_management import sql_executing_queries
import asyncio

async def result():
    import pandas as pd
    res= await sql_executing_queries.querying_tables_item_data('ohlc60_eth_perp_json')
    df=pd.DataFrame(res)
    print (df)
    return res

if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(result())
        

    except Exception as error:
        print(error)
