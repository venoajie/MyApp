# -*- coding: utf-8 -*-

# installed
from dataclassy import dataclass
from utils import system_tools, pickling, string_modification
from risk_management import spot_hedging
from portfolio.deribit import myTrades_management
import asyncio
from loguru import logger as log

def catch_error (error) -> list:
    """
    """
    system_tools.catch_error_message(error)
    
@dataclass(unsafe_hash=True, slots=True)
class CheckDataIntegrity ():

    '''
    '''       
    label: str 
    currency: str 
    position_per_instrument: list
    my_trades_open: list
            
        
    async def myTrades_from_db (self) -> list:
        """
        """

        try:
            my_trades_path_open_recovery = system_tools.provide_path_for_file ('myTrades', 
                                                                           self.currency,
                                                                           'open-recovery-point'
                                                                           )
            
            my_trades_path_open  = system_tools.provide_path_for_file ('myTrades', 
                                                                           self.currency,
                                                                           'open'
                                                                           )
            my_trades_from_db_recovery = pickling.read_data (my_trades_path_open_recovery)
            my_trades_from_db_regular = pickling.read_data (my_trades_path_open)
            return {'db_recover': my_trades_from_db_recovery,
                    'db_regular': my_trades_from_db_regular}
        
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
                # get the earliest transaction time stamp
                
                my_trades_from_db_min_time_stamp =  min ([o['timestamp'] for o in my_trades_from_db_recovery ])-1
                
                # use the earliest time stamp to fetch data from exchange
                fetch_my_trades_from_system_from_min_time_stamp_to_now = await self.my_trades (my_trades_from_db_min_time_stamp, server_time)
                
                # compare data from exchanges. Pick only those have not recorded at system yet
                filtered_data_from_my_trades_from_exchange = \
                    string_modification.find_unique_elements (fetch_my_trades_from_system_from_min_time_stamp_to_now, 
                                                            my_trades_from_db_recovery
                                                            )
                # redistribute the filtered data into db
                my_trades_from_exchange = myTrades_management.MyTrades (filtered_data_from_my_trades_from_exchange)
                my_trades_from_exchange.distribute_trade_transaction(self.currency)
            
        except Exception as error:
            catch_error (error)
                                 
    async def compare_inventory_per_db_vs_system (self) -> int:
        
        '''
        #! MULTI LABEL?
        ''' 
        try:
            position_per_instrument = self.position_per_instrument

            spot_hedged = spot_hedging.SpotHedging (self.label,
                                                    self.my_trades_open
                                                    )
                
            actual_hedging_size = spot_hedged.compute_actual_hedging_size()
            
            if position_per_instrument:
                actual_hedging_size_system = position_per_instrument ['size']
                
                return  actual_hedging_size_system - actual_hedging_size 
            else:
                return  0 - actual_hedging_size 
            
        except Exception as error:
            catch_error (error)
                                 
    async def update_myTrades_file_as_per_comparation_result (self, server_time: int) -> list:
        
        '''
        ''' 
        try:
            size_difference = await self.compare_inventory_per_db_vs_system()
            log.debug (f'{size_difference=}')
            
            
            if size_difference == 0:
                my_trades_path_open = await self.myTrades_from_db ()            
                my_trades_path_open_reguler = my_trades_path_open ['reguler']            
                pickling.replace_data (my_trades_path_open_reguler, True)
            
            if size_difference != 0:
                await self.rearrange_my_trades_consistency (server_time)

        except Exception as error:
            catch_error (error)
                             