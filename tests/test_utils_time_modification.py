from src.utilities import time_modification
import datetime
from datetime import datetime, timezone#, timedelta


local_date_time = datetime.now()
expected_utc_date_time = str(
    local_date_time.astimezone().astimezone(
        timezone.utc
        ).replace(
            tzinfo=None
            )
    )
actual_utc_date_time = str(time_modification.translate_current_local_date_time_to_utc())
print (expected_utc_date_time)
print (actual_utc_date_time)
print (datetime(actual_utc_date_time))
print (datetime(expected_utc_date_time))
print((actual_utc_date_time) == (expected_utc_date_time))

def test_convert_time_to_unix  ():
    test_data_transaction_time1 = '2022-12-14 15:33:29.858518'
    test_data_transaction_time2 = '2022-12-14 15:34:29.858518'
    test_data_transaction_time3 = '2022-12-14 15:34:30.858518'
    assert time_modification.convert_time_to_unix (test_data_transaction_time1) == 1671032009858
    # test result one minute = 60000
    assert (time_modification.convert_time_to_unix (test_data_transaction_time2) -  time_modification.convert_time_to_unix (test_data_transaction_time1) == 60000)
    # test result one second = 1000
    assert (time_modification.convert_time_to_unix (test_data_transaction_time3) -  time_modification.convert_time_to_unix (test_data_transaction_time2) == 1000)
        
def test_get_current_local_date_time  ():
    result = time_modification.get_current_local_date_time()
    assert isinstance(result, datetime) 
    
def test_translate_current_local_date_time_to_utc  ():
    import pytest
    
    # https://stackoverflow.com/questions/46914222/how-can-i-assert-lists-equality-with-pytest
    
    local_date_time = datetime.now()
    expected_utc_date_time = str(
        local_date_time.astimezone().astimezone(
            timezone.utc
            ).replace(
                tzinfo=None
                )
        )
    actual_utc_date_time = str(time_modification.translate_current_local_date_time_to_utc())

    assert len(actual_utc_date_time) == len(expected_utc_date_time)
    assert (actual_utc_date_time) == pytest.approx (expected_utc_date_time)
    #assert all([a == b for a, b in zip(actual_utc_date_time, expected_utc_date_time)])
        
def test_time_delta_between_two_times  ():

    start_time = '2020-01-01 00:00:00'
    end_time = '2020-01-01 01:00:00'
    time_format = 'utc'
    expected_time_delta = {'seconds': 3600, 'hours': 1.0, 'days': 0.041666666666666664}
    assert (time_modification.time_delta_between_two_times (time_format, 
                                                            start_time, 
                                                            end_time
                                                            )) == expected_time_delta

    start_time = '2020-01-01 00:00:00'
    end_time   = '2020-01-01 01:00:00'
    start_time = time_modification.convert_time_to_unix (start_time) 
    end_time = time_modification.convert_time_to_unix (end_time)
    time_format = 'unix-ms'
    #expected_time_delta = {'seconds': 10, 'hours': 0.002777777777777778, 'days': 10}
    
    assert (time_modification.time_delta_between_two_times (time_format, 
                                                            start_time, 
                                                            end_time
                                                            )) == expected_time_delta
    time_format = 'unix'
    #expected_time_delta = {'seconds': 10, 'hours': 0.002777777777777778, 'days': 10}
    
    assert (time_modification.time_delta_between_two_times (time_format, 
                                                            start_time, 
                                                            end_time
                                                            )) == expected_time_delta
