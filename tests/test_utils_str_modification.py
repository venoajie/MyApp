# -*- coding: utf-8 -*-
import pytest

from utilities.string_modification import extract_currency_from_text


@pytest.mark.parametrize("text, expected", [
    ("incremental_ticker.BTC-PERPETUA", "btc"),
    ("incremental_ticker.BTC-4OCT24", "btc"),
    ("chart.trades.BTC-4OCT24", "btc"),
    ("chart.trades.BTC-PERPETUAL.1", "btc"),
    ("chart.trades.BTC-PERPETUAL.1D", "btc"),
    ("user.portfolio.eth", "eth"),
    ("user.changes.any.ETH.raw", "eth"),
    ])
def test_check_if_closing_size_will_exceed_the_original(text,
                                                        expected):

    result = extract_currency_from_text(text,)

    assert result == expected

