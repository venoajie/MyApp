
import asyncio
import random

tes= [['BTC-30AUG24', 'BTC-6SEP24', 'BTC-27SEP24', 'BTC-27DEC24', 'BTC-28MAR25', 'BTC-27JUN25', 'BTC-PERPETUAL'], ['ETH-30AUG24', 'ETH-6SEP24', 'ETH-27SEP24', 'ETH-27DEC24', 'ETH-28MAR25', 'ETH-27JUN25', 'ETH-PERPETUAL']]
test= ['],['.join(x) for x in tes]
print (test)

test = str(tes).replace('], [', '').replace('],[', '')
print (test)

print ([
    x
    for xs in tes
    for x in xs
])
print ([test])
