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
    
def provide_path_for_file (file_name: str, folder1: str = None, folder2: str = None)-> None:
    '''
    '''   
    from pathlib import Path
    
    current_os = get_platform ()
    
    # Set root equal to  current folder
    root:str = Path(".")
    
    # COmbine root + folders
    my_path_linux: str = root / folder1 if folder2 == None else  root / folder1 / folder2
    my_path_win:str = root / "src" / folder1 if folder2 == None else  root / "src" / folder1 / folder2
    
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
        

if __name__ == "__main__":
    try:
        
        folder1 = "market_data"
        folder2 = "deribit"
        file_name = "test.pkl"
        path = provide_path_for_file (file_name, "market_data", "deribit")
        print (path)

    except (KeyboardInterrupt, SystemExit):
        import sys
        sys.exit()

    except Exception as error:
        print (error)