#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from time import sleep

none_data=[None, 0, []]

def get_platform ()-> str:

    '''
    https://www.webucator.com/article/how-to-check-the-operating-system-with-python/
    https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
    '''   
    
    platforms:dict = {
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
    
def provide_path_for_file (end_point: str, marker: str = None, status: str =None, method: str =None)-> str:
    '''
    marker: currency, instrument, other
    end_point: orders, myTrades
    method: web/manual, api/bot
    status: open, closed
    '''   
    from pathlib import Path
    
    current_os = get_platform ()
    
    # Set root equal to  current folder
    root:str = Path(".")
    
    exchange = None
    
    if  bool([o for o in ['orders', 'myTrades', 'portfolio','positions'] if (o in end_point)])  :
        sub_folder = 'portfolio'
        exchange = 'deribit'
        
    if bool([o for o in ['ordBook', 'index', 'instruments','currencies','ohlc']  if (o in end_point)])  :
        sub_folder = 'market_data'
        exchange = 'deribit'
        
    if bool([o for o in ['openInterestHistorical', 'openInterestHistorical', 'openInterestAggregated']  if (o in end_point)])  :
        sub_folder = 'market_data'
    
    if  marker != None:
        
        file_name =  (f'{marker.lower()}-{end_point}')  
            
        if  status != None:
            file_name =  (f'{file_name}-{status}')  
            
        if  method != None:
            file_name =  (f'{file_name}-{method}')  
                
    else:
        file_name =  (f'{end_point}')
        
    file_name =  (f'{file_name}.pkl')
    
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
            