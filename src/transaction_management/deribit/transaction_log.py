# -*- coding: utf-8 -*-

# installed
from loguru import logger as log
from dataclassy import dataclass

# user defined formula
from db_management.sqlite_management import (
    executing_query_based_on_currency_or_instrument_and_strategy as get_query,
    insert_tables)

from utilities.string_modification import (
    remove_dict_elements,)

def telegram_bot_sendtext(bot_message, purpose: str = "general_error") -> None:
    from utilities import telegram_app

    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

async def saving_transaction_log (transaction_log_trading, 
                                  archive_db_table,
                                  transaction_log,
                                  first_tick_fr_sqlite, 
                                  ) -> None:
    """_summary_

    Args:
        trades (_type_): _description_
        orders (_type_): _description_
    """
    

    #log.debug (f"transaction_log {transaction_log}")
    for transaction in transaction_log:
        
        modified_dict= remove_dict_elements(transaction,"info")
                    
        timestamp_log= modified_dict ["timestamp"]
        
        type_log= modified_dict ["type"]
                    
        if timestamp_log > first_tick_fr_sqlite:

            custom_label= f"custom-{type_log.lower()}-{timestamp_log}"
            
            if "trade" in type_log or "delivery" in type_log:
            
                if "trade" in type_log:
                
                    tran_id_log= modified_dict ["trade_id"]

                    instrument_name_log= modified_dict ["instrument_name"]
                    
                    column_list: str="label", "trade_id"
                    
                    from_sqlite_open= await get_query (archive_db_table, 
                                                        instrument_name_log, 
                                                        "all", 
                                                        "all", 
                                                        column_list)                                       
                    
                    label_log= [o["label"] for o in from_sqlite_open if tran_id_log in o["trade_id"]]
                                                            
                    if label_log !=[]:
                        modified_dict.update({"label": label_log[0]})
                    
                    else:
                        modified_dict.update({"label": custom_label})
            
                if "delivery" in type_log:
                    modified_dict.update({"label": custom_label})
                    
                #log.debug (f"transaction_log_json {modified_dict}")
                await insert_tables(transaction_log_trading, modified_dict)
            
            else:
                modified_dict.update({"label": custom_label})
                #log.debug (f"transaction_log_json {modified_dict}")
                table= f"transaction_log_json"
                await insert_tables(table, modified_dict)
