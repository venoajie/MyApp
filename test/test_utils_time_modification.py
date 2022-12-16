from utils import time_modification

def test_convert_time_to_unix  ():
    test_data_transaction_time1 = '2022-12-14 15:33:29.858518'
    test_data_transaction_time2 = '2022-12-14 15:34:29.858518'
    test_data_transaction_time3 = '2022-12-14 15:34:30.858518'
    assert time_modification.convert_time_to_unix (test_data_transaction_time1) == 1671032009858
    # test result one minute = 60000
    assert (time_modification.convert_time_to_unix (test_data_transaction_time2) -  time_modification.convert_time_to_unix (test_data_transaction_time1) == 60000)
    # test result one second = 1000
    assert (time_modification.convert_time_to_unix (test_data_transaction_time3) -  time_modification.convert_time_to_unix (test_data_transaction_time2) == 1000)
        