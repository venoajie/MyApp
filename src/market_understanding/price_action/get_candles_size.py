from db_management import sql_executing_queries
import asyncio

async def get_dataframe_from_ohlc_tables(tables: str ='ohlc60_eth_perp_json'):
    import pandas as pd
    res= await sql_executing_queries.querying_tables_item_data(tables)
    df= pd.DataFrame(res)
    df['candle_size']=df['high']-df['low']
    df['body_size']=df['open']-df['close']
    tes= df.rolling(10).mean()
    print(tes)
    return df

if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(get_dataframe_from_ohlc_tables('ohlc60_eth_perp_json'))
        

    except Exception as error:
        print(error)
