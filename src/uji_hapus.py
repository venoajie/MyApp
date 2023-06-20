from db_management import sql_executing_queries
import asyncio

async def result():
    from market_understanding.price_action import get_candles_size
    candles= await get_candles_size.get_dataframe_from_ohlc_tables('ohlc60_eth_perp_json')
    print (candles)
    return candles

if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(result())
        

    except Exception as error:
        print(error)
