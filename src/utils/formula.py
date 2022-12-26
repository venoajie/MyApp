#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
from functools import lru_cache
import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from functools import wraps
from unittest import result
from loguru import logger as log
from unsync import unsync

none_data=[None, 0, []]

def check_environment()->bool:

    '''
    https://stackoverflow.com/questions/42665882/how-does-the-python-script-know-itself-running-in-nohup-mode
    '''   
    import signal

    if signal.getsignal(signal.SIGHUP) == signal.SIG_DFL:  # default action
        print("No SIGHUP handler")
    else:
        print("In nohup mode")
        
def is_float(num: any)->bool:

    '''
    https://www.programiz.com/python-programming/examples/check-string-number
    '''   
    if num == None:
        return None      
    
    else:
        try:
            float(num)
            return True
        except ValueError:
            return False
        
def convert_str_to_float_single (data_json: list)->list:
    

    '''
    https://stackoverflow.com/questions/21193682/convert-a-string-key-to-int-in-a-dictionary
            Return and rtype: 
            Catatan: 
    '''   

    if isinstance(data_json, dict):
        return [{k: float(eval(v)) if is_float(v) else v for k, v in data_json.items()}]
    if isinstance(data_json, list):
        data_json=data_json[0]
        return [{k: float(v) if is_float(v) else v for k, v in data_json.items()}]
                
@unsync        
def convert_str_to_float_ (data_json: list)->object:
    

    '''
    https://stackoverflow.com/questions/21193682/convert-a-string-key-to-int-in-a-dictionary
            Return and rtype: 
            Catatan: 
    ''' 
    excluded = ['id', 'reduceOnly', 'postOnly', 'liquidation','ioc','market','future','type','side', 'orderId', 'time','tradeId','feeCurrency',
                'liquidity', 'baseCurrency', 'quoteCurrency','coin']
    
    if isinstance(data_json, dict):
        data_json = [data_json]
        
    if len (data_json)== 1:
        #data_json=data_json[0]
        return convert_str_to_float_single (data_json)
    
    if len (data_json) > 1:
        list_combination = []
        for i in data_json:
            
            if isinstance(i, dict):
                data_json=[data_json]
                position = {k: float(v) if (is_float(v) and (k) not in excluded) else v for k, v in i.items()}
            if isinstance(i, list):
                position = {k: float(v) if (is_float(v) and (k) not in excluded) else v for k, v in i.items()}
            list_combination.append(position)
        
        return list_combination
                
def convert_str_to_float (data_json: list)->list:
    
    '''
    ''' 
    result_ = convert_str_to_float_ (data_json)
    return result_.result()
    
def sleep_and_restart_program (idle: float)->None:
    from time import sleep
    import os,sys
    
    if idle != None:     
        
        print (f" sleep for {idle} seconds")
        sleep (idle)
        
    print (f"restart")
    python = sys.executable
    os.execl(python, python, * sys.argv)
    
def log_error (sub_account: str, underlying_aktif: str, error: str, idle: float = None)->None:

    '''  
        # Capture & emit error message
        # Send error message to telegram server
        # https://medium.com/pipeline-a-data-engineering-resource/prettify-your-python-logs-with-loguru-a7630ef48d87

    '''        
    import traceback
    from utils import telegram_app
    from loguru import logger as log

    telegram_app.telegram_bot_sendtext (f'{sub_account} {underlying_aktif} \n {error} \n \n {traceback.format_exc()}')
    log.add("out.log", backtrace=True, diagnose=True)  # Caution, may leak sensitive data in prod
    log.debug (f'{error}')
    log.error (traceback.format_exc())
    
    if idle != None:
        log.critical (f"restart {idle} seconds after error")
        sleep_and_restart_program(idle)
        
def print_json(data):
    import json
    print( json.dumps(data, indent=2))

def restart_program():
    import sys, os
    python = sys.executable
    os.execl(python, python, * sys.argv)

def restart_sleep(func):

    '''  
        # Restart sleep untuk setiap ekseksi fungsi

    '''        
    @wraps(func)
    def actual_func(*args, **kwargs):
        """Inner function within decorator, which does the actual work"""
        from time import sleep
        import os,sys       
#        print(f'Fungsi {func.__name__} tereksekusi')
        func(*args, **kwargs)
        print(f"Sleep 10 detik") 
        sleep (10)
        print(f"Restart") 
        python = sys.executable
        os.execl(python, python, * sys.argv)

    return actual_func

def kill_app():

    """
    # https://stackoverflow.com/questions/17856928/how-to-terminate-process-from-python-using-pid
    """         
    
    from os import getpid
    from sys import argv, exit
    import psutil

    myname = argv[0]
    mypid = getpid()
    for process in psutil.process_iter():
        if process.pid != mypid:
            for path in process.cmdline():
                if myname in path:
                    log.critical ("process found")
                    process.terminate()
                    exit()


def remove_redundant_elements (data):
    
    '''  
    # https://www.codegrepper.com/code-examples/python/remove+redundant+elements+in+list+python
    # https://python.plainenglish.io/how-to-remove-duplicate-elements-from-lists-without-using-sets-in-python-5796e93e6d43
    
    '''      
    
    return sorted(set(data))    

def transform_underlying_from_or_to_perpetual (symbol: str, default: str)-> str:

    '''
    # default = underlying/perpetual/spot
    '''        
    symbol_len = len (symbol)
    perp_to_underlying_len = len (symbol)-5 # 5 : -PERP
    last_is_perp = symbol[4:] == 'PERP'
    last_is_underlying = "-" not in symbol
    
    if default == 'underlying':
        if last_is_perp:
            symbol = f'{(symbol[0:perp_to_underlying_len])}'
    
    if default == 'perpetual':
        if last_is_underlying:
            symbol = f'{symbol}-PERP'
        
    return symbol
            

#! FORMULA TERKAIT WAKTU  ********************************************************************************************************************************************************************

def convert_time_to_utc (transaction_time: str= None, hours_diff_with_utc: float= None):

    '''
        # Mendapatkan waktu UTC/JKT saat ini (now) dengan UTC sebagai patokan
                
            Args:
                param (None): None
            
            Return and rtype: 
                waktu utc/jkt dalam format yyyy/mm/dd --> dict
            
            Referensi: 
                https://stackoverflow.com/questions/3327946/how-can-i-get-the-current-time-now-in-utc    
    '''        
    from datetime import datetime

    # menarik waktu lokal saat ini
    local_datetime = datetime.now()
    
    # waktu lokal saat ini ditranslasi ke utc
    utc= local_datetime.astimezone().astimezone(timezone.utc).replace(tzinfo=None)
    if transaction_time != None:
        transaction_time_ = datetime.fromisoformat(transaction_time)
        transaction_time = transaction_time_.astimezone().astimezone(timezone.utc).replace(tzinfo=None)
        utc_f_transaction_time = (transaction_time+timedelta( hours= 0 if hours_diff_with_utc == None else hours_diff_with_utc )).strftime('%Y-%m-%d %H:%M:%S.%f')
        utc_p_transaction = datetime.strptime(utc_f_transaction_time,'%Y-%m-%d %H:%M:%S.%f')
    
    # diformat text
    utc_f = utc.strftime('%Y-%m-%d %H:%M:%S.%f')    
    #print(f'H {utc_f=}')
    utc_f_jkt = (utc+timedelta( hours=7 )).strftime('%Y-%m-%d %H:%M:%S.%f') #JKT selisih 7 jam dengan utc
    
    # diformat waktu agar bisa diolah lebih lanjut di fungsi berikutnya 
    utc_p = datetime.strptime(utc_f,'%Y-%m-%d %H:%M:%S.%f')
    utc_p_jkt = datetime.strptime(utc_f_jkt,'%Y-%m-%d %H:%M:%S.%f')

    return {'utc_now':utc_p,
            'utc_now_day_name':utc.strftime("%A"),
            'jkt_now':utc_p_jkt,
            'transaction_time':None if transaction_time == None else utc_p_transaction}
    
#! will be deleted, replaced by convert_time_to_unix *******************************************************************************************
def convert_utc_to_unix_ (waktu):

    '''  
        # Mendapatkan waktu unix
                
            Args:
                param1 (Date): Waktu dalam format '%Y-%m-%d %H:%M:%S.%f'
            
            Return and rtype: 
                waktu dalam format UNIX (microseconds) utc/jkt --> int
            
            Referensi: 
                https://stackoverflow.com/questions/41856393/time-data-conversion-missing-microseconds-in-gm-time-python
                https://stackoverflow.com/questions/10611328/parsing-datetime-strings-containing-nanoseconds
                https://stackoverflow.com/questions/58939822/python-does-not-match-format-y-m-dthmsz-f

    '''        

    try:

        try:
            waktu_= 0 if waktu == 0 else  datetime.fromisoformat(waktu)     
            waktu =0 if waktu == 0 else waktu_.strftime('%Y-%m-%d %H:%M:%S.%f')
            waktu = 0 if waktu == 0 else datetime.strptime(waktu,'%Y-%m-%d %H:%M:%S.%f') 

            microsecs = waktu.microsecond 

        except:
            microsecs = waktu.microsecond # menarik microsecond untuk dihitung terpisah
            
    except Exception as error:
        import traceback
        from loguru import logger as log
        log.error(f"{error}")
        log.error(traceback.format_exc())
    
    unix= int((calendar.timegm(waktu.timetuple())*1000000+microsecs)/1000) 
            
    return unix
#! ****************************************************************************************************************


def convert_time_to_unix (time):

    '''  
        # Mendapatkan waktu unix
                
            Args:
                param1 (Date): Waktu dalam format '%Y-%m-%d %H:%M:%S.%f'
            
            Return and rtype: 
                waktu dalam format UNIX (microseconds) utc/jkt --> int
            
            Referensi: 
                https://stackoverflow.com/questions/41856393/time-data-conversion-missing-microseconds-in-gm-time-python
                https://stackoverflow.com/questions/10611328/parsing-datetime-strings-containing-nanoseconds
                https://stackoverflow.com/questions/58939822/python-does-not-match-format-y-m-dthmsz-f

    '''        

    try:

        try:
                
            time_= 0 if time == 0 else  datetime.fromisoformat(time)  
            time =0 if time == 0 else time_.strftime('%Y-%m-%d %H:%M:%S.%f')
            time = 0 if time == 0 else datetime.strptime(time,'%Y-%m-%d %H:%M:%S.%f') 
            microsecs = time.microsecond 

        except:
            microsecs = time.microsecond # menarik microsecond untuk dihitung terpisah
            
    except Exception as error:
        import traceback
        from loguru import logger as log
        print (f"{error}")
        print (traceback.format_exc())
        

    except Exception as error:
        log_error ('formula', 'convert_time_to_unix', error, None)
    
    unix= int((calendar.timegm(time.timetuple())*1000000+microsecs)) 
            
    return unix


def waktu_modifikasi_file_terakhir (nama_file: str):

    """Menghitung selisih  antara waktu saat ini dengan 
            waktu saat pembuatan file
            
            Referensi: 
                https://stackoverflow.com/questions/27580917/get-file-modification-date

    """
    import os

    #menarik waktu saat ini
    unix_now = convert_time_to_utc()["utc_now"]
    
    #waktu saat ini ditranslasi ke unix
    unix_now=convert_utc_to_unix(unix_now)
    
    try:
        #menarik waktu modifikasi file
        mtime = os.path.getmtime(nama_file)
    except OSError:
        mtime = 0
        
    #menyesuaikan format waktu modifikasi file    
    last_modified_date = datetime.fromtimestamp(mtime)
    
    #waktu modifikasi file ditranslasi ke unix
    last_modified_date_unix = convert_utc_to_unix(last_modified_date)
    
    #menghitung delta waktu modifikasi file vs waktu saat ini
    time_delta = 0 if last_modified_date_unix in none_data else int(unix_now - last_modified_date_unix)

    return time_delta

def time_delta(unix_aplikasi: int):

    """Menghitung selisih  antara waktu saat ini dengan 
            waktu saat transaksi dalam format unix microseconds

    :Args:
                param1 (float): waktu saat ini
                param2 (float): waktu saat transaksi
    return and rtype: (float) selisih param 1 dan param2.

    """

    utc_now = convert_time_to_utc()["utc_now"]
    
    unix_now=convert_utc_to_unix(utc_now)
    
    time_delta = 0 if unix_aplikasi in none_data else int(unix_now - unix_aplikasi)

    return time_delta


def time_delta_between_now_and_transaction_time_both_in_utc (transaction_time: str)-> float:

    """Menghitung selisih  antara waktu saat ini dengan 
            waktu saat transaksi 

    """
    now_time_utc = convert_time_to_utc ()['utc_now']
    transaction_time_utc = convert_time_to_utc (transaction_time)['transaction_time']
    
    #time_delta in seconds
    time_delta = 0 if transaction_time in none_data else ((transaction_time_utc - now_time_utc ).total_seconds())
    
    return {'seconds': time_delta,
            'hours': time_delta/3600,
            'days': time_delta/3600/24}
            
def time_delta_between_two_times (start_time: str, end_time: str)-> float:

    """Menghitung selisih  antara waktu 2 waktu

    """
    transaction_time_start_utc = convert_time_to_utc (start_time)['transaction_time']
    transaction_time_end_utc = convert_time_to_utc (end_time)['transaction_time']
    
    #time_delta in seconds
    time_delta =  ((transaction_time_end_utc - transaction_time_start_utc ).total_seconds())
    
    return {'seconds': time_delta,
            'hours': time_delta/3600,
            'days': time_delta/3600/24}

def timeit_wrapper(func: object ):

    '''  
        # Menghitung waktu yang diperlukan untuk menyelesaikan satu tugas
                
            Args:
                param1 (Date): Fungsi yang dites 
            
            Return and rtype: 
                Nama modul, fungsi, waktu
            
            Referensi: 
                https://towardsdatascience.com/making-python-programs-blazingly-fast-c1cd79bd1b32

    '''        
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()  # Alternatively, you can use time.process_time()
        func_return_val = func(*args, **kwargs)
        end = time.perf_counter()
        print('{0:<10}.{1:<8} : {2:<8}'.format(func.__module__, func.__name__, end - start))
        return func_return_val
    return wrapper
#! FORMULA TERKAIT REKAYASA FORMAT **************************************************************************************************************************************************************

def presisi_pembulatan (angka):

    '''
        # Menghitung berapa angka di belakang koma untuk keperluan pembulatan 
                
            Args:
                param1 (float): yang ingin dibulatkan (float: 0.xx atau 1e4)
            
            Return and rtype: 
                berapa angka di belakang koma --> int
            
            Referensi: 
                https://stackoverflow.com/questions/38847690/convert-float-to-string-in-positional-format-without-scientific-notation-and-fa
                https://stackoverflow.com/questions/3886402/how-to-get-numbers-after-decimal-point
                https://stackoverflow.com/questions/26231755/count-decimal-places-in-a-float
    ''' 

    from numpy import format_float_positional as format_float

    angka = str(format_float(angka))
    
    return  int( angka[::-1].find('.')) 

def rounding(variable, TICK, presisi):

    '''
        # Pembulatan berdasarkan tick per instrumen agar sesuai dengan standar harga exchange
                
            Args:
                param1 (float): angka yang akan dibulatkan
                param2 (float): tick angka
                param3 (int): presisi hasil pembulatan
            
            Return and rtype: 
                hasil pembulatan --> float
            
    ''' 
    rounding = (int(variable / TICK))    
    rounding = float(round(rounding * TICK, presisi))

    return rounding

def merge(dic1,dic2):
    #Merge two Dictionaries
    dic3=dic1.copy()
    dic3.update(dic2)
    return dic3    


#Copyright 2021 Fabian Bosler

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation 
# files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, 
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom 
# the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
# Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS 
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from functools import wraps
import time
import logging
import random

logger = logging.getLogger(__name__)


def retry(exceptions, total_tries=4, initial_wait=0.5, backoff_factor=2, logger=None):
    """
    calling the decorated function applying an exponential backoff.
    Args:
        exceptions: Exception(s) that trigger a retry, can be a tuple
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier (e.g. value of 2 will double the delay each retry).
        logger: logger to be used, if none specified print
https://towardsdatascience.com/are-you-using-python-with-apis-learn-how-to-use-a-retry-decorator-27b6734c3e6
    """
    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = total_tries + 1, initial_wait
            while _tries > 1:
                try:
                    log(f'{total_tries + 2 - _tries}. try:', logger)
                    return f(*args, **kwargs)
                except exceptions as e:
                    _tries -= 1
                    print_args = args if args else 'no args'
                    if _tries == 1:
                        msg = str(f'Function: {f.__name__}\n'
                                  f'Failed despite best efforts after {total_tries} tries.\n'
                                  f'args: {print_args}, kwargs: {kwargs}')
                        log(msg, logger)
                        raise
                    msg = str(f'Function: {f.__name__}\n'
                              f'Exception: {e}\n'
                              f'Retrying in {_delay} seconds!, args: {print_args}, kwargs: {kwargs}\n')
                    log(msg, logger)
                    time.sleep(_delay)
                    _delay *= backoff_factor

        return func_with_retries
    return retry_decorator


def log(msg, logger=None):
    if logger:
        logger.warning(msg)
    else:
        print(msg)


def test_func(*args, **kwargs):
    rnd = random.random()
    if rnd < .2:
        raise ConnectionAbortedError('Connection was aborted :(')
    elif rnd < .4:
        raise ConnectionRefusedError('Connection was refused :/')
    elif rnd < .8:
        raise ConnectionResetError('Guess the connection was reset')
    else:
        return 'Yay!!'

@lru_cache(maxsize=None)    
def open_json_file (nama_file):

    import json
    try:            
        with  open(nama_file, "r") as file:
            contents = json.load(file)
            file.close()

    except Exception as error:
        import traceback
        from loguru import logger as log
        log.error(f"{error}")
        log.error(traceback.format_exc())
    return contents


def save_json_file (filename, data):
    import json    
        
    try:
        with  open(filename, "w") as file:
            json.dump(data, file)
            
    except Exception as error:
        import traceback
        from loguru import logger as log
        log.error(f"{error}")
        log.error(traceback.format_exc())
            
    finally:
        file.close()     

def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    import math
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

if __name__ == '__main__':
    # wrapper = retry((ConnectionAbortedError), tries=3, delay=.2, backoff=1, logger=logger)
    # wrapped_test_func = wrapper(test_func)
    # print(wrapped_test_func('hi', 'bye', hi='ciao'))
    #modif=waktu_modifikasi_file_terakhir('funding_rates.json')
    #print(modif)
    #wrapper_all_exceptions = retry(Exception, total_tries=2, logger=logger)
    #wrapped_test_func = wrapper_all_exceptions(test_func)
    #print(wrapped_test_func('hi', 'bye', hi='ciao'))
    l = 'book.BTC-16DEC22.none.20.100ms'
    l = "".join(list(l) [5:][:-14])[:3]
    print (l)