#!/usr/bin/env python
# -*- coding: utf-8 -*-

import calendar
from datetime import datetime, timedelta, timezone

none_data=[None, 0, []]

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
            'jkt_now':utc_p_jkt,
            'transaction_time':None if transaction_time == None else utc_p_transaction}

def check_day_name (time: datetime)->str:

    '''
    check day name based on time given
    '''    
    # time in datetime format    
    try:
        
        return time.strftime("%A")
    
    # time in text format
    except:
        # convert string to time format
        time_in_time_format = datetime.strptime(time,'%Y-%m-%d %H:%M:%S.%f')
        return time_in_time_format.strftime("%A")
            
    
def convert_time_to_unix (time)-> int:

    '''  
        # Get time  (milliseconds since the UNIX epoch)
                
            Args:
                param1 (Date): Waktu dalam format '%Y-%m-%d %H:%M:%S.%f'
                one minute = 60000
            
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
                
    return int((calendar.timegm(time.timetuple())*1000000+microsecs)/1000) 


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



if __name__ == '__main__':
    transaction_time = '2022-12-14 15:33:29.858518'
    print (convert_time_to_unix(transaction_time))
