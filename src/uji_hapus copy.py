
def extract_currency_from_text(words: str) -> str:
    """
    Extracting currency from channel message
    
     some variables:
     chart.trades.BTC-PERPETUAL.1
     incremental_ticker.BTC-4OCT24
    """
    if "."in words:
          filter1= (words.partition('.')[2]).lower()
          print(filter1)
          
          if "."in filter1:
            filter1= (filter1.partition('.')[2]).lower()
            print(filter1)
      
    else:
          filter1= (words.partition('.')[0]).lower()
        
    return (filter1.partition('-')[0]).lower()

print(extract_currency_from_text("chart.trades.BTC-PERPETUAL.1"))
        