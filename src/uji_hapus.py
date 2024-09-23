
def extract_currency_from_text(words: str) -> str:
    """
    Extracting currency from channel message
    """

    return (words.partition('-')[0]).lower()

print (extract_currency_from_text("ETH-20SEP24"))
print (extract_currency_from_text("ETH-PERPETUAL"))
print (extract_currency_from_text("BTC-27SEP24"))
print (extract_currency_from_text("BTC"))
