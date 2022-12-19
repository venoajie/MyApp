from utils import string_modification

def test_extract_currency_from_text  ():
    websocket_message_channel_user_portfolio_BTC = 'user.portfolio.BTC'
    websocket_message_channel_user_portfolio_ETH = 'user.portfolio.ETH'
    
    websocket_message_channel_user_trades_ETH = 'user.trades.future.ETH.100ms'
    websocket_message_channel_user_trades_BTC = 'user.trades.future.BTC.100ms'
    
    websocket_message_channel_user_orders_BTC = 'user.orders.future.BTC.raw'
    websocket_message_channel_user_orders_ETH = 'user.orders.future.ETH.raw'
    
    websocket_message_channel_book_BTC = 'book.BTC-29SEP23.none.20.100ms'
    websocket_message_channel_book_ETH = 'book.ETH-27JAN23.none.20.100m'
    
    websocket_message_channel_chart_BTC = 'chart.trades.BTC-PERPETUAL.1'
    websocket_message_channel_chart_ETH = 'chart.trades.ETH-PERPETUAL.1'
    
    websocket_message_channel_price_index_BTC = 'deribit_price_index.btc_usd'
    websocket_message_channel_price_index_ETH = 'deribit_price_index.eth_usd'
    
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_portfolio_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_portfolio_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_trades_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_trades_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_orders_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_user_orders_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_book_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_book_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_chart_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_chart_ETH) == 'eth'
    assert string_modification.extract_currency_from_text (websocket_message_channel_price_index_BTC) == 'btc'
    assert string_modification.extract_currency_from_text (websocket_message_channel_price_index_ETH) == 'eth'
    
def test_remove_redundant_elements  ():
    elements = ['BTC', 'BTC', 'BTC', 'ETH', 'ETH', 'LTC']
    assert string_modification.remove_redundant_elements (elements) == ['BTC', 'ETH', 'LTC']
    
def test_extract_integers_from_text  ():
    assert string_modification.extract_integers_from_text ('hedging spot-open-1671189554374') == 1671189554374    
    assert string_modification.extract_integers_from_text ('hedging spot-open') == []    
    assert string_modification.extract_integers_from_text ('1671189554374') == 1671189554374