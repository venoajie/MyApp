import string
 
test_string = 'incremental_ticker.BTC-4OCT24'
 
# omitting K lengths
res =  [word.strip(string.punctuation) for word in test_string.split() if word.strip(string.capwords).isalnum()]

print(res)
 