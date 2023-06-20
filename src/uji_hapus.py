from db_management import sql_executing_queries
import asyncio

async def result():
    res= await sql_executing_queries.query_data_pd('ohlc60_eth_perp_json')
    print (res)
    return res

if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(result())
        

    except Exception as error:
        print(error)
