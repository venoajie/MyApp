#!/usr/bin/env/python
# -*- coding: utf-8 -*-

# built ins

import asyncio
import requests


# installed
import aioschedule as schedule
import time
from loguru import logger as log
import aiohttp
from dataclassy import dataclass, fields
# user defined formula
from configuration import config
from configuration.label_numbering import get_now_unix_time
from db_management.sqlite_management import (
    back_up_db_sqlite,
    executing_query_with_return,
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    insert_tables, 
    querying_arithmetic_operator,)
from market_understanding.technical_analysis import (
    insert_market_condition_result,)
from strategies.futures_spread import FutureSpreads  
from strategies.config_strategies import paramaters_to_balancing_transactions
from transaction_management.deribit.api_requests import (
    get_currencies,
    get_instruments,
    get_server_time,
    ModifyOrderDb)
from transaction_management.deribit.transaction_log import (saving_transaction_log,)
from utilities.pickling import (
    replace_data,
    read_data,)
from utilities.string_modification import (
    remove_redundant_elements, 
    transform_nested_dict_to_list,
    parsing_label,)
from utilities.system_tools import (
    catch_error_message, 
    provide_path_for_file,)
from websocket_management.allocating_ohlc import (
    ohlc_end_point, 
    ohlc_result_per_time_frame,
    last_tick_fr_sqlite,)
from websocket_management.ws_management import (
    get_config,)
from websocket_management.cleaning_up_transactions import (
    clean_up_closed_transactions,
    ensuring_db_reconciled_each_other,
    get_unrecorded_trade_and_order_id)

def catch_error(error, idle: int = None) -> list:
    """ """
    catch_error_message(error, idle)
    
async def get_instruments_from_deribit(currency) -> float:
    """ """

    result = await get_instruments(currency)

    return result


async def future_spreads(currency) -> float:
    """ """
    from strategies.futures_spread import get_futures_combo_instruments

    result = await get_futures_combo_instruments (currency)

    return result

async def get_currencies_from_deribit() -> float:
    """ """

    result = await get_currencies()

    print(f"get_currencies {result}")

    return result

async def back_up_db():
    await back_up_db_sqlite ()

async def current_server_time() -> float:
    """ """
    current_time = await get_server_time()
    return current_time["result"]


def get_label_transaction_net(my_trades_open_remove_closed_labels: list) -> float:
    """ """
    return (
        []
        if my_trades_open_remove_closed_labels == []
        else remove_redundant_elements(
            [
                parsing_label(o["label"])["transaction_net"]
                for o in my_trades_open_remove_closed_labels
            ]
        )
    )


@dataclass(unsafe_hash=True, slots=True)
class RunningStrategy (ModifyOrderDb):

    """ """

    sub_account_summary: list
    my_trades_currency: list
    orders_currency: list
    leverage: float= fields 
    modify_order_and_db: object = fields 
    # Async Event Loop
    def __post_init__(self):
        self.leverage =  sum([abs(o["amount"]) for o in self.my_trades_currency])
        self.modify_order_and_db: str = ModifyOrderDb(self.sub_account_id)
        log.error (f"leverage {self.leverage}")
        #log.error (f"sub_account_summary {self.sub_account_summary}")

    async def running_strategies (self,
                                 currency) -> dict:
        
        file_toml = "config_strategies.toml"
        
        config_app = get_config(file_toml)
        
        strategy_attributes = config_app["strategies"]
        
        active_strategies =   [o["strategy_label"] for o in strategy_attributes if o["is_active"]==True]
              
        while True:
            
            for strategy in active_strategies:
                log.error (f"strategy {strategy}")
                
                my_trades_currency_strategy = [o for o in self.my_trades_currency if strategy in (o["label"]) ]
                                
                strategy_params= [o for o in strategy_attributes if o["strategy_label"] == strategy][0]   
                                
                if "futureSpread" in strategy:
                    
                    future_spreads = FutureSpreads (strategy,
                                             strategy_params,
                                             currency,
                                             my_trades_currency_strategy)
                    await future_spreads.is_send_exit_order_allowed()
                
def parse_dotenv(sub_account) -> dict:
    return config.main_dotenv(sub_account)


async def running_strategy() -> None:
    """ """
    sub_account_id = "deribit-147691"

    file_toml = "config_strategies.toml"
        
    config_app = get_config(file_toml)

    tradable_config_app = config_app["tradable"]
    
    currencies= [o["spot"] for o in tradable_config_app] [0]
            
    try:
        for currency in currencies:
            
            trade_db_table= "my_trades_all_json"
            
            order_db_table= "orders_all_json"                       
                                        
            column_list= "instrument_name", "position", "timestamp"      
            
            currency_lower = currency.lower()
            
            transaction_log_trading= f"transaction_log_{currency_lower}_json"                                              
            
            from_transaction_log = await get_query (transaction_log_trading, 
                                                        currency, 
                                                        "all", 
                                                        "all", 
                                                        column_list)                                       
                        
            column_trade: str= "instrument_name","label", "combo_id", "amount", "price","side"

            sub_account_summary = reading_from_pkl_data ("sub_accounts",
                                                        currency)
            
            if sub_account_summary:           
                sub_account_summary[0]
                        
                my_trades_currency: list= await get_query(trade_db_table, 
                                                            currency, 
                                                            "all", 
                                                            "all", 
                                                            column_trade)

                column_order= "instrument_name","label","order_id","amount","timestamp"
                
                log.error (f"my_trades_currency {my_trades_currency}")
                
                orders_currency = await get_query(order_db_table, 
                                                        currency, 
                                                        "all", 
                                                        "all", 
                                                        column_order)     
                
                running= RunningStrategy (sub_account_id,
                                        sub_account_summary,
                                        my_trades_currency,
                                        orders_currency)
                
                await running.running_strategies(currency)
                
                await running.modify_order_and_db.resupply_sub_accountdb (currency)
                
                instrument_from_sub_account = [o["instrument_name"] for o  in sub_account_summary[0] ["positions"]]
                
                for instrument_name in instrument_from_sub_account:
                    
                    archive_db_table= f"my_trades_all_{currency_lower}_json"       
                    
                    await running.modify_order_and_db.update_trades_from_exchange (currency,
                                                                                   archive_db_table,
                                                                                   5)
                    
                    await clean_up_closed_transactions (instrument_name, 
                                                        trade_db_table)

                    db_reconciled =  ensuring_db_reconciled_each_other (sub_account_summary,
                                                                        instrument_name,
                                                                        my_trades_currency,
                                                                        orders_currency,
                                                                        from_transaction_log)
                                                           
                    log.warning (f"db_reconciled {db_reconciled}")
                    if not db_reconciled["sum_trade_from_log_and_db_is_equal"]: 
                        
                        unrecorded_transactions = await get_unrecorded_trade_and_order_id (instrument_name)
                        #log.warning (f"unrecorded_transactions {unrecorded_transactions}")
                        
                        for transaction  in unrecorded_transactions:
                            #log.error (f"transaction {transaction}")
                            await insert_tables (trade_db_table, 
                                                transaction)

                        currency_lower = currency.lower()
                        
                        archive_db_table= f"my_trades_all_{currency_lower}_json"
                        
                        transaction_log_trading= f"transaction_log_{currency_lower}_json"
                        
                        await running.modify_order_and_db.resupply_transaction_log (currency_lower,
                                                                                    transaction_log_trading,
                                                                                    archive_db_table
                                                                                    )
                
                    if not db_reconciled["len_order_from_sub_account_and_db_is_equal"]:
                        pass
                
    except Exception as error:
        
        catch_error_message(
            error, 10, "app"
        )


def reading_from_pkl_data(end_point, currency, status: str = None) -> dict:
    """ """

    path: str = provide_path_for_file(end_point, currency, status)

    data = read_data(path)

    return data



async def get_private_data(sub_account: str = "deribit-147691") -> list:
    """
    Provide class object to access private get API
    """

    
    return ModifyOrderDb (sub_account)
    #return api_request

async def get_transaction_log(currency: str, start_timestamp: int, count: int= 1000) -> list:
    """ """

    private_data = await get_private_data()

    result_transaction_log: dict = await private_data.get_transaction_log(currency,
                                                                          start_timestamp, 
                                                                          count)
    
    result_transaction_log_to_result = result_transaction_log["result"]
    

    return [] if result_transaction_log_to_result  == []\
        else result_transaction_log_to_result["logs"]

async def run_every_60_seconds() -> None:
    """ """

    from websocket_management.cleaning_up_transactions import count_and_delete_ohlc_rows

    await count_and_delete_ohlc_rows()
    #await back_up_db()


async def run_every_15_seconds() -> None:
    """ """

    ONE_PCT = 1 / 100
    WINDOW = 9
    RATIO = 0.9
    THRESHOLD = 0.01 * ONE_PCT
       
    file_toml = "config_strategies.toml"
        
    config_app = get_config(file_toml)

    tradable_config_app = config_app["tradable"]
    
    currencies= [o["spot"] for o in tradable_config_app] [0]
    
    end_timestamp=     get_now_unix_time()  
    
    for currency in currencies:
        
        instrument_name= f"{currency}-PERPETUAL"

        await insert_market_condition_result(instrument_name, WINDOW, RATIO)
        
        time_frame= [3,5,15,60,30,"1D"]
            
        ONE_SECOND = 1000
        
        one_minute = ONE_SECOND * 60
        
        WHERE_FILTER_TICK: str = "tick"
        
        for resolution in time_frame:
            
            table_ohlc= f"ohlc{resolution}_{currency.lower()}_perp_json" 
                        
            last_tick_query_ohlc_resolution: str = querying_arithmetic_operator (WHERE_FILTER_TICK, "MAX", table_ohlc)

            #data_from_ohlc1_start_from_ohlc_resolution_tick: str = 
            
            start_timestamp: int = await last_tick_fr_sqlite (last_tick_query_ohlc_resolution)
            
            if resolution == "1D":
                delta= (end_timestamp - start_timestamp)/(one_minute * 60 * 24)
        
            else:
                delta= (end_timestamp - start_timestamp)/(one_minute * resolution)
                        
            if delta > 1:
                end_point= ohlc_end_point(instrument_name,
                                resolution,
                                start_timestamp,
                                end_timestamp,
                                )

                ohlc_request = requests.get(end_point).json()["result"]
                
                result = [o for o in transform_nested_dict_to_list(ohlc_request) \
                    if o["tick"] > start_timestamp][0]
                
                await ohlc_result_per_time_frame (instrument_name,
                                                resolution,
                                                result,
                                                table_ohlc,
                                                WHERE_FILTER_TICK, )
            
                
                await insert_tables(table_ohlc, result)
        

async def check_and_save_every_60_minutes():

    try:

        get_currencies_all = await get_currencies_from_deribit()
        currencies = [o["currency"] for o in get_currencies_all["result"]]
        #        print(currencies)

        for currency in currencies:

            instruments = await get_instruments_from_deribit(currency)
            # print (f'instruments {instruments}')

            my_path_instruments = provide_path_for_file("instruments", currency)

            replace_data(my_path_instruments, instruments)

        my_path_cur = provide_path_for_file("currencies")

        replace_data(my_path_cur, currencies)
        # catch_error('update currencies and instruments')

    except Exception as error:
        catch_error(error)


if __name__ == "__main__":

    try:
        # asyncio.get_event_loop().run_until_complete(check_and_save_every_60_minutes())
        schedule.every().hour.do(check_and_save_every_60_minutes)
        

        schedule.every().hour.do(back_up_db)
        schedule.every(1).seconds.do(running_strategy)
        schedule.every(15).seconds.do(run_every_15_seconds)
        #schedule.every(3).seconds.do(run_every_3_seconds)
        #schedule.every(5).seconds.do(run_every_5_seconds)
        schedule.every(60).seconds.do(run_every_60_seconds)

        schedule.every().day.at("08:01").do(check_and_save_every_60_minutes)
        schedule.every().day.at("08:05").do(check_and_save_every_60_minutes)

        loop = asyncio.get_event_loop()

        while True:
            loop.run_until_complete(schedule.run_pending())
            time.sleep(0.91)

    except Exception as error:
        print(error)
        catch_error(error, 30)
