import asyncio
from configuration.label_numbering import get_now_unix_time
from strategies import  hedging_spot

from loguru import logger as log
from strategies.config_strategies import hedging_spot_attributes,preferred_spot_currencies,paramaters_to_balancing_transactions

from utilities.number_modification import get_closest_value

from websocket_management.cleaning_up_transactions import (
    reconciling_between_db_and_exchg_data, 
    clean_up_closed_transactions,
    get_unrecorded_order_id,
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
            sum_my_trades_instrument, size_from_position
            )

        if not size_is_consistent:
            log.critical (f"BALANCING-START")
            
            await cancel_the_cancellables("open")
            
            balancing_params=paramaters_to_balancing_transactions()
            
            max_transactions_downloaded_from_exchange=balancing_params["max_transactions_downloaded_from_exchange"]
            
            max_closed_transactions_downloaded_from_sqlite=balancing_params["max_closed_transactions_downloaded_from_sqlite"]
            
            trades_from_exchange = await get_my_trades_from_exchange(max_transactions_downloaded_from_exchange, currency)
            
            trades_from_sqlite_closed = await executing_general_query_with_single_filter(
                "my_trades_closed_json", instrument_ticker, max_closed_transactions_downloaded_from_sqlite, "id"
                )
            from_sqlite_closed_order_id = [o["order_id"] for o in trades_from_sqlite_closed]
            
            log.warning(f"from_sqlite_closed_order_id {instrument_ticker} {from_sqlite_closed_order_id}")
            log.info(f"trades_from_sqlite_closed {trades_from_sqlite_closed}")
            unrecorded_order_id = await get_unrecorded_order_id(
                instrument_ticker,
                my_trades_instrument, 
                trades_from_sqlite_closed, 
                trades_from_exchange
                )
            #log.debug(f"unrecorded_order_id {unrecorded_order_id}")
            await reconciling_between_db_and_exchg_data(instrument_ticker,
                trades_from_exchange, unrecorded_order_id
                )
            log.warning (f"CLEAN UP CLOSED TRANSACTIONS")
            await clean_up_closed_transactions(instrument_ticker)
            log.critical (f"BALANCING-DONE")
                                                        
        else:                                                
            # obtain spot equity
            equity: float = portfolio[0]["equity"]
            
            ticker: list = reading_from_db("ticker", instrument_ticker)
            
            index_price: float = ticker[0]["index_price"]
                                                
            if ticker !=[] and index_price is not None and equity >0:
            
                tick_TA=  max([o["tick"] for o in TA_result_data])
                
                server_time=     get_now_unix_time()  
                
                delta_time= server_time-tick_TA
                
                delta_time_seconds=delta_time/1000                                                
                
                log.debug (f" delta_time_seconds {delta_time_seconds} tick_TA {tick_TA} server_time {server_time} {delta_time_seconds<120}")

                if delta_time_seconds < 120:#ensure freshness of ta
                    
                    notional: float = compute_notional_value(index_price, equity)
                        
                    best_ask_prc: float = ticker[0]["best_ask_price"]                                                    
                    
                    hedging = hedging_spot.HedgingSpot(strategy_label)
                    log.warning (f"A")
                    
                    send_order: dict = (
                    await hedging.is_send_and_cancel_open_order_allowed(
                        currency,
                        instrument_ticker,
                        notional,
                        index_price,
                        best_ask_prc,
                        server_time,
                        TA_result_data
                    )
                )
                    
                    log.warning (f"A")
                    log.debug(f"if_order_is_true {send_order} {instrument_ticker} ")
                    
                    if send_order["order_allowed"]:
                        await if_order_is_true(send_order, instrument_ticker)
                        await if_cancel_is_true(send_order)

                    log.critical (f"OPENING HEDGING-DONE")    
                                                            
                    
                    
                    my_trades_open_hedging = [o for o in my_trades_instrument if "open" in (o["label"])\
                        and "hedgingSpot" in (o["label"]) ]

                    if my_trades_open_hedging !=[]:
                    
                        log.critical (f"CLOSING HEDGING-START {instrument_ticker}")
                                    
                        best_bid_prc: float = ticker[0]["best_bid_price"]
                        get_prices_in_label_transaction_main = [o["price"] for o in my_trades_open_hedging]
                        closest_price = get_closest_value(get_prices_in_label_transaction_main, best_bid_prc)
                        nearest_transaction_to_index = [o for o in my_trades_open_hedging if o["price"] == closest_price]
                        
                        send_closing_order: dict = await hedging.is_send_exit_order_allowed(
                            TA_result_data,
                            index_price,
                            best_ask_prc,
                            best_bid_prc,
                            nearest_transaction_to_index,
                        )
                        await if_order_is_true(send_closing_order, instrument_ticker)

            log.critical (f"CLOSING HEDGING-DONE")
            tes=1/0
            log.error (tes)
                

if __name__ == "__main__":

    try:
        loop = asyncio.get_event_loop()

        while True:
            loop.run_until_complete(test())

    except Exception as error:
        print(error)