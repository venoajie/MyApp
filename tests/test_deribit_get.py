# -*- coding: utf-8 -*-
import src.deribit_get as get_dbt
import asyncio
import pytest


def parse_dotenv(sub_account) -> dict:
    from src.configuration import config

    return config.main_dotenv(sub_account, "test.env")


sub_account: str = "deribit-147691"
client_id: str = parse_dotenv(sub_account)["client_id"]
client_secret: str = parse_dotenv(sub_account)["client_secret"]
currency: str = "eth"

connection_url: str = "https://www.deribit.com/api/v2/"


async def get_private_data() -> list:
    """
    Provide class object to access private get API
    """

    return get_dbt.GetPrivateData(connection_url, client_id, client_secret, currency)

@pytest.mark.asyncio
async def test_get_open_orders_byCurrency():
    private_data = await get_private_data()

    open_orders_byCurrency = await private_data.get_open_orders_byCurrency()

    assert list(open_orders_byCurrency) == [
        "jsonrpc",
        "id",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]


@pytest.mark.asyncio
async def test_get_user_trades_by_currency():
    private_data = await get_private_data()
    user_trades_by_currency = await private_data.get_user_trades_by_currency()

    assert list(user_trades_by_currency) == [
        "jsonrpc",
        "id",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]


@pytest.mark.asyncio
async def test_get_account_summary():
    private_data = await get_private_data()
    account_summary = await private_data.get_account_summary()

    assert list(account_summary) == [
        "jsonrpc",
        "id",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]


@pytest.mark.asyncio
async def test_get_positions():
    private_data = await get_private_data()
    positions = await private_data.get_positions()

    assert list(positions) == [
        "jsonrpc",
        "id",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]


@pytest.mark.asyncio
async def test_get_subaccounts():
    private_data = await get_private_data()
    subaccounts = await private_data.get_subaccounts()

    assert list(subaccounts) == [
        "jsonrpc",
        "id",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]


@pytest.mark.asyncio
async def test_get_server_time():
    server_time = await get_dbt.get_server_time(connection_url)

    assert list(server_time) == [
        "jsonrpc",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]


@pytest.mark.asyncio
async def test_get_currencies():
    currencies = await get_dbt.get_currencies(connection_url)

    assert list(currencies) == [
        "jsonrpc",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]

@pytest.mark.asyncio
async def test_get_get_instruments():
    get_instruments = await get_dbt.get_instruments(connection_url, "eth")

    assert list(get_instruments) == [
        "jsonrpc",
        "result",
        "usIn",
        "usOut",
        "usDiff",
        "testnet",
    ]


@pytest.mark.asyncio
async def test_ohlc():
    resolution = 15
    qty_candles = 100
    ohlc = await get_dbt.get_ohlc(
        connection_url, "eth-perpetual", resolution, qty_candles
    )

    assert list(ohlc) == ["usOut", "usIn", "usDiff", "testnet", "result", "jsonrpc"]


@pytest.mark.asyncio
async def test_get_open_interest_aggregated_ohlc():
    resolution = "m5"
    connection_url: str = "https://open-api.coinglass.com/public/v2/"

    ohlc = await get_dbt.get_open_interest_aggregated_ohlc(
        connection_url, "eth-perpetual", resolution
    )

    assert list(ohlc) == ["code", "msg", "success"]


@pytest.mark.asyncio
async def test_get_open_interest_symbol():
    connection_url: str = "https://open-api.coinglass.com/public/v2/"

    open_interest = await get_dbt.get_open_interest_symbol(connection_url, "eth")

    assert list(open_interest) == ["code", "msg", "success"]


@pytest.mark.asyncio
async def test_telegram_bot_sendtext():
    bot_message = "test with purpose-general error"
    purpose = "general_error"

    result = await get_dbt.telegram_bot_sendtext(bot_message, purpose)

    assert list(result) == ["ok", "result"]

    bot_message = "test with None purpose"

    result = await get_dbt.telegram_bot_sendtext(bot_message)

    assert list(result) == ["ok", "result"]

    bot_message = "test with purpose-failed order"
    purpose = "failed_order"

    result = await get_dbt.telegram_bot_sendtext(bot_message, purpose)
    assert list(result) == ["ok", "result"]
