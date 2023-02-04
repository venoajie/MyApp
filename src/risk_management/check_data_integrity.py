# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
import asyncio

# user defined formula 
from utilities import system_tools, pickling, string_modification
from portfolio.deribit import myTrades_management
from loguru import  logger as log

def catch_error (error) -> list:
    ''' 
        
    Fetch error handling
    
    Args:
        error (dict): error message from system.
        
    Returns:
        list: error message.

    '''
    system_tools.catch_error_message(error)
        
def telegram_bot_sendtext (bot_message, 
                           purpose: str = 'general_error'
                           ) -> None:
    from utilities import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, 
                                              purpose
                                              )

async def myTrades_originally_from_db (currency) -> list:
    """
    """

    try:
        none_data = [None,[]]
        my_trades_path_open_recovery = system_tools.provide_path_for_file ('myTrades', 
                                                                            currency,
                                                                            'open-recovery-point'
                                                                            )
        
        my_trades_path_open  = system_tools.provide_path_for_file ('myTrades', 
                                                                    currency,
                                                                    'open'
                                                                    )

        my_trades_from_db_recovery = pickling.read_data (my_trades_path_open_recovery)
        my_trades_from_db_regular = pickling.read_data (my_trades_path_open)

        return {'db_recover': my_trades_from_db_recovery,
                'time_stamp_to_recover': [] if my_trades_from_db_recovery in none_data\
                    else min ([o['timestamp'] for o in my_trades_from_db_recovery ])-1,
                'path_recover': my_trades_path_open_recovery,
                'path_regular': my_trades_path_open,
                'db_regular': my_trades_from_db_regular
                }
    
    except Exception as error:
        catch_error (error)
        
@dataclass(unsafe_hash=True, slots=True)
class CheckTradeIntegrity ():

    '''
    '''       
    currency: str 
    positions_from_get: list
    my_trades_open_from_db: list
    my_selected_trades_open_from_system: list
            
    async def myTrades_from_db (self) -> list:
        """
        """

        try:
            return await myTrades_originally_from_db (self.currency)
        
        except Exception as error:
            catch_error (error)
                             
    async def rebuilt_db_myTrades_open (self, 
                                               server_time: int
                                               ) -> None:
        """
        
        """
                
        try:
            my_trades_from_db = await self.myTrades_from_db ()
            my_trades_from_db_recovery = my_trades_from_db['db_recover']
            log.warning(my_trades_from_db_recovery)
            
            if my_trades_from_db_recovery:
                
                # compare data from exchanges. 
                # Pick only those have not recorded at system yet
                filtered_data_from_my_trades_from_exchange =  string_modification.find_unique_elements (
                    self.my_selected_trades_open_from_system,  
                        my_trades_from_db_recovery
                        )
                log.error(filtered_data_from_my_trades_from_exchange)
                
                # redistribute the filtered data into db
                my_trades_from_exchange = myTrades_management.MyTrades (
                    filtered_data_from_my_trades_from_exchange
                    )
                
                my_trades_from_exchange.distribute_trade_transaction(self.currency)
            
        except Exception as error:
            catch_error (error)
                                 
    def net_position (self, 
                      selected_transactions: list
                      )-> float:
        
        '''
        '''    
        from utilities import number_modification                
        return number_modification.net_position (selected_transactions)
                                 
    async def compare_inventory_per_db_vs_get (self) -> int:
        
        '''
        ''' 

        try:
            
            size_from_get_db = self.net_position (self.positions_from_get)
            size_from_trading_db = self.net_position (self.my_trades_open_from_db)
            log.critical (f'size_from_get_db {size_from_get_db} size_from_trading_db {size_from_trading_db}')
            
            if size_from_get_db and size_from_trading_db:
                
                difference = size_from_trading_db - size_from_get_db 
                
                if difference !=0:
                    info= (f'SIZE DIFFERENT size per trading db {size_from_trading_db} size from get db {size_from_get_db} \n ')
                    telegram_bot_sendtext(info) 
                #log.warning (f'difference {difference}')
                
                return  difference
            else:
                if size_from_get_db == []  and size_from_trading_db == [] :
                    return 0
                if size_from_get_db == []:
                    return size_from_trading_db  
                if size_from_trading_db == []:
                    return  0 - size_from_get_db 
            
        except Exception as error:
            catch_error (error)
                                 
    async def update_myTrades_file_as_per_comparation_result (self
                                                              ) -> list:
        
        '''
        ''' 
        try:
            size_difference = await self.compare_inventory_per_db_vs_get()
            #log.critical (f'size_difference {size_difference}')
            
            if size_difference == 0:
                my_trades_path_open = await self.myTrades_from_db ()            
                pickling.replace_data (my_trades_path_open ['path_recover'] , 
                                       my_trades_path_open ['db_regular'] , 
                                       True
                                       )
            
            if size_difference != 0:
                await self.rebuilt_db_myTrades_open ()

        except Exception as error:
            catch_error (error)

                             
                             
async def main_enforce_my_trade_db_integrity (
                                            currency,
                                            positions_from_get,
                                            my_trades_open_from_db,
                                            my_selected_trades_open_from_system
                                            ):

    '''
    '''       
    
    my_trades_open_mgt: object = myTrades_management.MyTrades (my_trades_open_from_db)     
    my_trades_open_mgt.distribute_trade_transaction (currency)
            
    trade_integrity =  CheckTradeIntegrity (currency,
                                           positions_from_get,
                                           my_trades_open_from_db,
                                           my_selected_trades_open_from_system
                                           )
    await trade_integrity.update_myTrades_file_as_per_comparation_result ()
    
                                     
@dataclass(unsafe_hash=True, slots=True)
class CheckOrderIntegrity ():

    '''
    '''       
    currency: str 
    open_order_from_get: list
    open_order_from_db: list
            
    async def compare_open_order_per_db_vs_get(self) -> int:
        
        '''
        ''' 

        try:
            
            both_sources_are_equivalent =  self.open_order_from_get == self. open_order_from_db
            log.critical (f'both_sources_are_equivalent {both_sources_are_equivalent} open_order_from_get {self.open_order_from_get} open_order_from_db {self. open_order_from_db}')
            
            if both_sources_are_equivalent == False:
                    info= (f'OPEN ORDER DIFFERENT open_order_from_get {self.open_order_from_get}  open_order_from_db {self. open_order_from_db} \n ')
                    telegram_bot_sendtext(info) 
                #log.warning (f'difference {difference}')
                
            return  both_sources_are_equivalent
                
            
        except Exception as error:
            catch_error (error)