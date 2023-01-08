# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
import asyncio

# user defined formula 
from utils import system_tools, pickling, string_modification
from portfolio.deribit import myTrades_management

def catch_error (error) -> list:
    """
    """
    system_tools.catch_error_message(error)
        
def telegram_bot_sendtext (bot_message, 
                           purpose: str = 'general_error'
                           ) -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)


async def myTrades_originally_from_db (currency) -> list:
    """
    """

    try:
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
                'time_stamp_to_recover': min ([o['timestamp'] for o in my_trades_from_db_recovery ])-1,
                'path_recover': my_trades_path_open_recovery,
                'path_regular': my_trades_path_open,
                'db_regular': my_trades_from_db_regular
                }
    
    except Exception as error:
        catch_error (error)
        
@dataclass(unsafe_hash=True, slots=True)
class CheckDataIntegrity ():

    '''
    '''       
    currency: str 
    position_per_instrument: list
    my_trades_open_from_db: list
    my_selected_trades_open_from_system: list
            
    async def myTrades_from_db (self) -> list:
        """
        """

        try:
            
            return await myTrades_originally_from_db (self.currency)
        
        except Exception as error:
            catch_error (error)
                             
    async def rearrange_my_trades_consistency (self, 
                                               server_time: int
                                               ) -> None:
        """
        """
                
        try:
            my_trades_from_db = await self.myTrades_from_db ()
            my_trades_from_db_recovery = my_trades_from_db['db_recover']
            
            if my_trades_from_db_recovery:
                
                # compare data from exchanges. Pick only those have not recorded at system yet
                filtered_data_from_my_trades_from_exchange = \
                    string_modification.find_unique_elements (self.my_selected_trades_open_from_system, 
                                                            my_trades_from_db_recovery
                                                            )
                # redistribute the filtered data into db
                my_trades_from_exchange = myTrades_management.MyTrades (filtered_data_from_my_trades_from_exchange)
                my_trades_from_exchange.distribute_trade_transaction(self.currency)
            
        except Exception as error:
            catch_error (error)
                                 
    def net_position (self, 
                      selected_transactions: list
                      )-> float:
        
        '''
        '''    
        from utils import number_modification                
        return number_modification.net_position (selected_transactions)
                                 
    async def compare_inventory_per_db_vs_system (self) -> int:
        
        '''
        #! MULTI LABEL?
        ''' 
        from loguru import logger as log
        try:
            position_per_instrument = self.position_per_instrument
            
            actual_hedging_size = self.net_position (self.my_trades_open_from_db)
            log.info (f'{actual_hedging_size=}')
            
            if position_per_instrument:
                actual_hedging_size_system = position_per_instrument ['size']
                
                difference = actual_hedging_size_system - actual_hedging_size 
                
                if difference !=0:
                    info= (f'SIZE DIFFERENT size per sistem {actual_hedging_size_system} size per db {actual_hedging_size} \n ')
                    telegram_bot_sendtext(info) 
                
                return  difference
            else:
                return  0 - actual_hedging_size 
            
        except Exception as error:
            catch_error (error)
                                 
    async def update_myTrades_file_as_per_comparation_result (self, 
                                                              server_time: int
                                                              ) -> list:
        
        '''
        ''' 
        try:
            size_difference = await self.compare_inventory_per_db_vs_system()
            
            if size_difference == 0:
                my_trades_path_open = await self.myTrades_from_db ()            
                pickling.replace_data (my_trades_path_open ['path_recover'] , 
                                       my_trades_path_open ['db_regular'] , 
                                       True
                                       )
            
            if size_difference != 0:
                await self.rearrange_my_trades_consistency (server_time)

        except Exception as error:
            catch_error (error)
                             