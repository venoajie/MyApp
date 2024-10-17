from cachetools import TTLCache
cache = TTLCache(maxsize=1, ttl=100)
cache['dog'] = 'dog'
a = cache['dog'] # dog
cache['dog']

#print (cache['dog'])    
#print (cache)