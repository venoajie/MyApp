from db_management import sql_executing_queries
import asyncio

async def get_dataframe_from_ohlc_tables(tables: str ='ohlc60_eth_perp_json'):
    """_summary_
https://www.tradingview.com/script/uuinZwsR-Big-Bar-Strategy/
    Args:
        tables (str, optional): _description_. Defaults to 'ohlc60_eth_perp_json'.

    Returns:
        _type_: _description_
    """
    import pandas as pd  
    
    barsizeThreshold=(.5)
    period=(10)
    mult=(2)
    
    res= await sql_executing_queries.querying_tables_item_data(tables)
    df= pd.DataFrame(res)
    df['candle_size']=df['high']-df['low']
    df['body_size']=abs(df['open']-df['close'])
    df['candle_size_avg']= df['candle_size'].rolling(period).mean()
    df['bigbar']=[(df['candle_size'] >= df['candle_size_avg']*mult) & (df['body_size']>df['candle_size']*barsizeThreshold)]

    return df

if __name__ == "__main__":

    try:
        asyncio.get_event_loop().run_until_complete(get_dataframe_from_ohlc_tables('ohlc60_eth_perp_json'))
        

    except Exception as error:
        print(error)
