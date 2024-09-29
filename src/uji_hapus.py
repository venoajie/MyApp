
from configuration.label_numbering import get_now_unix_time

from utilities import time_modification

now_utc = time_modification.convert_time_to_utc()["utc_now"]

one_second = 1000

one_minute = one_second * 60

server_time=     get_now_unix_time()  

last_tick= 1727611920000

delta= (server_time - last_tick)/(one_minute * 3)

print (f"server_time {server_time} now_utc {now_utc} delta {delta}")