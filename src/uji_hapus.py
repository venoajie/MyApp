from db_management import sql_executing_queries
import asyncio

async def result():
    res= await sql_executing_queries.query_data_pd('ohlc60_eth_perp_json')
    return res

if __name__ == "__main__":

    try:
        print (result)

    except Exception as error:
        print(error)
