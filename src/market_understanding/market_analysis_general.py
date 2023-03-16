# # -*- coding: utf-8 -*-

from datetime import date
from typing import Dict
from loguru import logger as log
from unsync import unsync
from dataclassy import dataclass
from functools import lru_cache

# https://betterprogramming.pub/improving-your-python-projects-with-type-hints-63cbdb16d97c


@dataclass(unsafe_hash=True, slots=True)
class Options:

    """
    # Options greek calculation
    +----------------------------------------------------------------------------------------------+

    +----------------------------------------------------------------------------------------------+
    #  References
        +  https://pypi.org/project/option-price/
        +  https://medium.datadriveninvestor.com/profit-from-volatility-with-long-straddles-90abb42c3370
        +  https://jfin-swufe.springeropen.com/articles/10.1186/s40854-021-00280-y
        +  https://pypi.org/project/py-vollib-vectorized/
        +  https://py-vollib-vectorized.readthedocs.io/en/latest/pkg_ref/iv.html
    +----------------------------------------------------------------------------------------------+

    """

    option_price: float
    underlying_price: float  # Underlying asset price
    strike: float  # Strike
    expiration_date: date  # (Annualized) time-to-expiration
    interest: float  # Interest free rate

    def time_to_expiration(self) -> float:
        from utils import formula

        transaction_time_utc = formula.convert_time_to_utc(self.expiration_date)[
            "transaction_time"
        ]
        now_time_utc = formula.convert_time_to_utc()["utc_now"]
        diff_time_seconds = (
            transaction_time_utc - now_time_utc
        ).total_seconds()  # https://stackoverflow.com/questions/4362491/how-do-i-check-the-difference-in-seconds-between-two-dates
        diff_time_hours = diff_time_seconds / 3600
        return diff_time_hours / 24

    def compute_implied_volatility(
        self, flag: str, model: str = "black_scholes"
    ) -> list:
        import py_vollib_vectorized

        if model == "black_scholes":
            return py_vollib_vectorized.vectorized_implied_volatility_black(
                self.option_price,
                self.underlying_price,
                self.strike,
                self.time_to_expiration(),
                self.interest,
                flag,
                return_as="numpy",
            )

    def compute_price(self, flag: str, model: str = "black_scholes") -> list:
        import py_vollib.black_scholes

        log.warning(
            f"{flag=} {self.option_price=} {self.strike=} {self.time_to_expiration ()=} {self.interest=} "
        )
        implied_vloatility = self.compute_implied_volatility(flag, model)

        return py_vollib.black_scholes.black_scholes(
            flag,
            self.option_price,
            self.strike,
            self.time_to_expiration(),
            self.interest,
            implied_vloatility,
        )

    def compute_price_array(self, flag: str) -> list:
        import py_vollib.black_scholes

        return py_vollib.black_scholes.black_scholes(
            flag,
            self.option_price,
            self.strike,
            self.time_to_expiration(),
            self.interest,
            self.compute_implied_volatility(flag),
            return_as="array",
        )

    # @lru_cache(maxsize=None)
    def get_all_greeks(self, flag: str, model: str, return_as: str) -> dict:
        from py_vollib_vectorized import get_all_greeks

        implied_vloatility = self.compute_implied_volatility(flag, model)

        return get_all_greeks(
            flag,
            self.option_price,
            self.strike,
            self.time_to_expiration(),
            self.interest,
            implied_vloatility,
            model=model,
            return_as=return_as,
        )

    # @lru_cache(maxsize=None)
    def get_all_greeks_df(self, df):
        from py_vollib_vectorized import price_dataframe

        df["Flag"] = ["c", "p"]
        df["S"] = 95
        df["K"] = [100, 90]
        df["T"] = 0.2
        df["R"] = 0.2
        df["IV"] = 0.2

        return price_dataframe(
            df,
            flag_col="Flag",
            underlying_price_col="S",
            strike_col="K",
            annualized_tte_col="T",
            riskfree_rate_col="R",
            sigma_col="IV",
            model="black_scholes",
            inplace=False,
        )


def is_contango_or_backwardation(
    futures_price: float, spot_or_perpetual_price: float
) -> Dict:
    margin = futures_price - spot_or_perpetual_price

    return {
        "margin_usd": [] if futures_price == [] else margin,
        "margin_pct": [] if futures_price == [] else margin / spot_or_perpetual_price,
        "contango": [] if futures_price == [] else margin > 0,
        "backwardation": [] if futures_price == [] else margin < 0,
    }


def fetch_and_combine_funding_rate_with_heatmap_result(dataframe):
    """
    # Combine df with instrument rate
            Return and rtype: dataframe
    """
    from market_data import fetch_next_funding

    try:
        # https://chrisalbon.com/code/python/data_wrangling/pandas_list_comprehension/

        dataframe["nextFundingRate"] = [
            (fetch_next_funding.fetch_next_funding_coin((o))["nextFundingRate"])
            for o in dataframe["future"]
        ]

    except Exception as error:
        import traceback

        log.error(f"{error}")
        log.error(traceback.format_exc())

    return dataframe


def query_sqlite(query_table, data_base="trading"):
    import sqlite_operation
    import pandas as pd

    with sqlite_operation.db_ops(data_base) as cur:
        # query = pd.read_sql_table('table_name', 'sqlite:///data.db')

        query = list(cur.execute(f"{query_table}"))
        return query


@unsync
def fetch_correlation_from_sqlite_(threshold) -> str:
    """ """

    import sqlite3
    import pandas as pd

    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect("trading")
    correl = pd.read_sql_query("SELECT * from correl_funding", con)
    correl = correl.to_dict("records")
    correl_above_threshold = [o for o in [o for o in correl if o["correl"] > threshold]]
    correl_below_threshold = [o for o in [o for o in correl if o["correl"] < threshold]]
    con.close()

    return {
        "correl_above_threshold": correl_above_threshold,
        "correl_all": correl,
        "correl_below_threshold": correl_below_threshold,
        "above_threshold_rate_positive": [
            o for o in [o for o in correl_above_threshold if o["nextFundingRate"] > 0]
        ],
        "above_threshold_rate_negative": [
            o for o in [o for o in correl_above_threshold if o["nextFundingRate"] < 0]
        ],
    }


def fetch_correlation_from_sqlite(threshold: float = 0):
    fetch_correlation_from_sqlite = fetch_correlation_from_sqlite_(threshold)

    return fetch_correlation_from_sqlite.result()


@unsync
def heatmap_and_funding_rate_(
    symbols: list,
    main_underlying: str = "BTC",
    time_frame: int = 3600,
    threshold: float = 0,
):
    """
    # Return heatmap/correlation for mentioned symbols above

            Return and rtype: A pandas Series
            Reference:  https://github.com/v0di/btc-correlation/blob/main/correlation_study.ipynb
                        https://www.linkedin.com/pulse/crypto-heatmap-cryptocurrencies-correlation-neven-dujmovic
    """

    import pandas as pd
    from dask import delayed, compute
    from utils import formula

    import random

    try:
        # initiate dask process
        fetch_dask = []

        # concatenate underlying into perpetual instrument
        symbol = f"{main_underlying}"
        symbol_main = f"{main_underlying}"
        ohlc = f"{symbol}_PERP_{time_frame}"

        # https://stackoverflow.com/questions/36028759/how-to-open-and-convert-sqlite-database-to-pandas-dataframe
        db = f"sqlite:///trading"
        query = pd.read_sql_table(f"{ohlc}", "sqlite:///trading")

        query_table = f"SELECT * FROM {ohlc}"
        # fetch ohlc main perpetual instrument

        ohlc_df = pd.read_sql_table(f"{ohlc}", "sqlite:///trading")
        ohlc_mid_main = pd.Series(ohlc_df["close"], dtype="float32")

        # ohlc_main = fetch_ohlc.OHLC (symbol, time_frame)
        # ohlc_df = ohlc_main. ohlc()
        # ohlc_mid_main = pd.Series(ohlc_df['close'], dtype='float32')

        # drop btc & stable coins
        symbols.remove(symbol_main)

        # fetch ohlc alts
        coeffs = {}
        random.shuffle(symbols)
        for symbol in symbols:
            symbol_underlying = formula.transform_underlying_from_or_to_perpetual(
                symbol, "underlying"
            )
            symbol = formula.transform_underlying_from_or_to_perpetual(
                symbol, "perpetual"
            )

            ohlc = f"{symbol_underlying}_PERP_{time_frame}"

            ohlc_df = pd.read_sql_table(f"{ohlc}", "sqlite:///trading")

            # ohlc_ = fetch_ohlc.OHLC (symbol, time_frame)
            # ohlc_df = ohlc_. ohlc()

            # Return the (symbol)'s daily percentage change
            coeffs[symbol] = ohlc_mid_main.corr(ohlc_df["close"], min_periods=300)

        # drop N/a results
        coeffs = pd.Series(coeffs).dropna()

        # sort results
        coeffs.sort_values(ascending=False, inplace=True)

        # to dataframe
        coeffs = pd.DataFrame(data=coeffs)

        # reset index
        coeffs = coeffs.iloc[::-1].reset_index()

        # rename header
        coeffs = coeffs.rename(columns={"index": "future", 0: "correl"})

        # combine with funding rate
        coeffs = fetch_and_combine_funding_rate_with_heatmap_result(coeffs)

        # preparing results
        correl_above_threshold = coeffs[coeffs["correl"] > threshold]
        correl_below_threshold = coeffs[coeffs["correl"] < threshold]

        # resume dask process
        results_dask = compute(*fetch_dask)

    except Exception as error:
        import traceback

        log.error(f"{error}")
        log.error(traceback.format_exc())

    return {
        "all_result": coeffs,
        "correl_above_threshold": correl_above_threshold,
        "correl_below_threshold": correl_below_threshold,
        "above_threshold_rate_positive": correl_above_threshold[
            correl_above_threshold["nextFundingRate"] > 0
        ],
        "above_threshold_rate_negative": correl_above_threshold[
            correl_above_threshold["nextFundingRate"] < 0
        ],
    }


def heatmap_and_funding_rate(
    symbols: list,
    main_underlying: str = "BTC",
    time_frame: int = 3600,
    threshold: float = 0,
):
    heatmap_and_funding_rate = heatmap_and_funding_rate_(
        symbols, main_underlying, time_frame, threshold
    )

    return heatmap_and_funding_rate.result()


if __name__ == "__main__":
    option_price = 604
    underlying_price = 23446  # Underlying asset price
    strike = 23400  # Strike
    time_to_expiration = "2022-08-20T00:00:00+00:00"  # (Annualized) time-to-expiration
    interest = 0  #

    flag = ["c", "p"]
    options = Options(
        option_price, underlying_price, strike, time_to_expiration, interest
    )

    price = options.compute_price(flag)
    log.warning(price)
    implied_volatility = options.compute_implied_volatility(flag)
    log.error(implied_volatility)
    greeks = options.get_all_greeks(flag, "black_scholes", "dict")
    log.critical(greeks)
