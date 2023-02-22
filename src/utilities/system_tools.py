#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from time import sleep

#none_data=[None, 0, []]

def parse_dotenv (domain_app: str = 'None')-> dict:    
    
    """
    https://www.python-engineer.com/posts/run-python-github-actions/
    """
    
    from os.path import join, dirname
    from dotenv import load_dotenv
    
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    client_id = None
    client_secret = None
    bot_token = None
    bot_chatid = None
            
    try:
        # linux/win env
        client_id = os.environ.get ('client_id')
        client_secret =  os.environ.get ('client_secret')
        
    except KeyError:
        
        # github env
        client_id = os.environ ('client_id')
        client_secret =  os.environ ('client_secret')
            
    return {'client_id': client_id,
            'client_secret': client_secret,
            'bot_token': bot_token,
            'bot_chatid': bot_chatid
            }
            
def get_platform ()-> str:

    '''
    https://www.webucator.com/article/how-to-check-the-operating-system-with-python/
    https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
    '''   
    
    platforms: dict = {
        'linux1' : 'linux',
        'linux2' : 'linux',
        'darwin' : 'OS X',
        'win32' : 'win'
        }
    
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]

def sleep_and_restart_program (idle: float)-> None:
    
    '''
    '''   
    
    if idle != None:     
        
        print (f" sleep for {idle} seconds")
        sleep (idle)
        
    print (f"restart")
    python = sys.executable
    os.execl(python, python, * sys.argv)
    
def provide_path_for_file (
                            end_point: str, 
                            marker: str = None, 
                            status: str =None, 
                            method: str =None
                           )-> str:
    '''
    marker: currency, instrument, other
    end_point: orders, myTrades
    status: open, closed
    method: web/manual, api/bot
    '''   
    from pathlib import Path
    
    current_os = get_platform ()
    
    # Set root equal to  current folder
    root:str = Path(".")
    
    exchange = None

    if  bool(
        [
            o for o in [
                'orders', 
                'myTrades', 
                'portfolio',
                'positions', 
                'sub_accounts'
                ] if (o in end_point)
            ]
        )  :
        
        sub_folder: str = 'portfolio'
        exchange: str = 'deribit'
        
    if bool(
        [
            o for o in [
                'ordBook', 
                'index', 
                'instruments',
                'currencies',
                'ohlc', 
                'futures_analysis', 
                'ticker-all',
                'ticker'
                         ]  if (o in end_point)
            ]
        ):
        
        sub_folder = 'market_data'
        exchange = 'deribit'
        
    if bool(
        [
            o for o in [
                'openInterestHistorical', 
                'openInterestHistorical', 
                'openInterestAggregated'
                         ]  if (o in end_point)
            ]
        )  :
        sub_folder: str = 'market_data'
    
    if  marker != None:
        
        file_name =  (f'{marker.lower()}-{end_point}')  
            
        if  status != None:
            file_name =  (f'{file_name}-{status}')  
            
        if  method != None:
            file_name =  (f'{file_name}-{method}')  
    
    else:
        file_name =  (f'{end_point}')

    if  '.env' in end_point:        
        sub_folder = 'configuration'
            
    file_name =  (f'{file_name}.pkl') if '.env' not in file_name else (f'{end_point}')
    
    # Combine root + folders
    my_path_linux: str = root / sub_folder if exchange == None else  root / sub_folder / exchange
    my_path_win:str = root / "src" / sub_folder if exchange == None else  root / "src" / sub_folder / exchange
    
    # Create target Directory if doesn't exist in linux
    if not os.path.exists(my_path_linux) and current_os =='linux':    

        os.makedirs(my_path_linux)
                        
    return (my_path_linux / file_name ) if get_platform () == 'linux' else (my_path_win / file_name)
    
    
def check_environment()->bool:

    '''
    https://stackoverflow.com/questions/42665882/how-does-the-python-script-know-itself-running-in-nohup-mode
    '''   
    import signal

    if signal.getsignal(signal.SIGHUP) == signal.SIG_DFL:  # default action
        print("No SIGHUP handler")
    else:
        print("In nohup mode")
        
def is_current_file_running (script)->bool:

    '''
    https://stackoverflow.com/questions/788411/check-to-see-if-python-script-is-running
    '''   
    import psutil

    for q in psutil.process_iter():
        if q.name().startswith('python'):
            if len(q.cmdline())>1 and script in q.cmdline()[1] and q.pid !=os.getpid():
                print("'{}' Process is already running".format(script))
                return True

    return False
            
        
def catch_error_message (error: str, 
                         idle: float = None,
                         message: str = None
                         )->None:

    '''  
        # Capture & emit error message
        # Send error message to telegram server
        # https://medium.com/pipeline-a-data-engineering-resource/prettify-your-python-logs-with-loguru-a7630ef48d87

    '''        
    import traceback
    from utilities import telegram_app
    from loguru import logger as log
    
    info = (f'{error} \n \n {traceback.format_exc()}')
    
    if message !=None:
        info =  (f'{message} \n \n {error} \n \n {traceback.format_exc()}')
        
    if error == True: # to respond 'def is_current_file_running'  result
        sys.exit (1)
        
    log.critical (f'{error}')
    log.debug (traceback.format_exc())
    
    log.add ("error.log", 
             backtrace=True, 
             diagnose=True
             )  # Caution, may leak sensitive data in prod
    
    telegram_app.telegram_bot_sendtext (info)
    
    if idle != None:
        log.info (f"restart {idle} seconds after error")
        sleep_and_restart_program (idle)
    else:
        sys.exit ()
        
        
        
    def db_membuka_koneksi(self,params):
        """Connect to a Postgres database."""
        import psycopg2.extras
        from psycopg2 import connect, sql
        import psycopg2.extras

        if self.conn is None:
            try:
               
                self.conn = psycopg2.connect(**params)
#                print(f'{self.conn=}')

            # bila terdapat error terkait koneksi ke postgres         
            except psycopg2.DatabaseError as e:
                raise e
            finally:
                print('Koneksi ke database terbuka')
        return self.conn

def open_connection_sqlite_ (self, db_file, params= None):
    """Connect to a sqlite database."""
    import sqlite3
    from sqlite3 import Error

    conn = None
    try:
        conn = sqlite3.connect(db_file)

    except Error as e:
        log.error (e)
    finally:
        if conn:
            conn.close()

def open_connection_sqlite (self, db_file, params= None):
    """Connect to a sqlite database."""
    connection_ = self. open_connection_sqlite_ (db_file, params= None)
    connection = connection_.result()
        