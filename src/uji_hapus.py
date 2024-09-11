import asyncio
from configuration.label_numbering import get_now_unix_time
from strategies import  hedging_spot

from loguru import logger as log
from strategies.config_strategies import hedging_spot_attributes,preferred_spot_currencies,paramaters_to_balancing_transactions

from utilities.number_modification import get_closest_value

from websocket_management.cleaning_up_transactions import (
    reconciling_between_db_and_exchg_data, 
    clean_up_closed_transactions,
)
from db_management.sqlite_management import (
    querying_table,
    executing_general_query_with_single_filter,
    )

from websocket_management.ws_management import (
    cancel_the_cancellables,
    if_order_is_true,
    if_cancel_is_true,
    compute_notional_value, 
    get_my_trades_from_exchange,
    reading_from_pkl_database,
    reading_from_db,
    is_size_consistent
    )

async def test():
    
    currencies = preferred_spot_currencies()
    number=0
    for currency in currencies:
        number = number+1
        log.critical (f"number {number}")
        instrument_ticker=f"{currency}-PERPETUAL"
        currency_upper=f"{currency.upper()}"
        log.critical (f" OPENING HEDGING-START-{instrument_ticker.upper()}")
                                                    
        TA_result_data_all = await querying_table("market_analytics_json")

        TA_result_data_only=  TA_result_data_all["list_data_only"]

        TA_result_data = [o for o in TA_result_data_only if currency_upper in o["instrument"]]
                                                                    
        strategy_label= hedging_spot_attributes()[0]["strategy"]

        ticker: list = reading_from_db("ticker", instrument_ticker)    
        
        index_price= ticker[0]["index_price"]            
        # gathering basic data
        reading_from_database: dict = await reading_from_pkl_database(currency)
                                            
        # get portfolio data
        portfolio: list = reading_from_database["portfolio"]

        my_trades_instrument: list=await executing_general_query_with_single_filter("my_trades_all_json", instrument_ticker)

        sum_my_trades_instrument = sum([o["amount"] for o in my_trades_instrument])

        # fetch positions for all instruments
        positions_all: list = reading_from_database["positions_from_sub_account"]

        #log.info(f"positions_all-recurring {positions_all} ")
        size_from_position: int = (
            0 if positions_all == [] else sum([o["size"] for o in positions_all if o["instrument_name"]==instrument_ticker])
        )

        size_is_consistent: bool = await is_size_consistent(
            sum_my_trades_instrument, size_from_position,instrument_ticker
            )

        if not size_is_consistent:

            log.critical (f"BALANCING-START")
            
            await cancel_the_cancellables("open")
            
            balancing_params=paramaters_to_balancing_transactions()
            
            max_transactions_downloaded_from_exchange=balancing_params["max_transactions_downloaded_from_exchange"]
            
            trades_from_exchange = await get_my_trades_from_exchange(max_transactions_downloaded_from_exchange, currency)

            await reconciling_between_db_and_exchg_data(instrument_ticker,
                trades_from_exchange)
            
            log.warning (f"CLEAN UP CLOSED TRANSACTIONS-START")
            await clean_up_closed_transactions(instrument_ticker)
            log.critical (f"BALANCING-DONE")
                

if __name__ == "__main__":

    try:
        loop = asyncio.get_event_loop()

        while True:
            loop.run_until_complete(test())

    except Exception as error:
        print(error)