
def extract_currency_from_text(words: str) -> str:
    """
    Extracting currency from channel message
    """
    if "."in words:
          filter1= (words.partition('.')[2]).lower()
    
    else:
          filter1= (words.partition('.')[0]).lower()
        
    return (filter1.partition('-')[0]).lower()

print(extract_currency_from_text("BTC-PERPETUAL"))
        