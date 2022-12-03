#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys
from time import sleep

none_data=[None, 0, []]

def get_platform()-> str:

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
    
def create_path_for_market_data_deribit_output (file_name: str)-> None:
    '''
    '''   
    from pathlib import Path
    
    current_os = get_platform ()
    
    # Set root equal to  current folder
    root:str = Path(".")
    
    my_path_linux: str = root / "market_data" / "deribit"

    # Create target Directory if doesn't exist
    if not os.path.exists(my_path_linux) and current_os =='linux':
        os.makedirs(my_path_linux)
                        
    my_path_linux:str = my_path_linux / file_name
    my_path_win:str = root / "src" / "market_data" /  "deribit" / file_name

    return my_path_linux if get_platform () == 'linux' else my_path_win
    
def check_environment()->bool:

    '''
    https://stackoverflow.com/questions/42665882/how-does-the-python-script-know-itself-running-in-nohup-mode
    '''   
    import signal

    if signal.getsignal(signal.SIGHUP) == signal.SIG_DFL:  # default action
        print("No SIGHUP handler")
    else:
        print("In nohup mode")