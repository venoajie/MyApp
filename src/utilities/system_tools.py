# -*- coding: utf-8 -*-

import os, sys
from time import sleep
import asyncio

def get_platform() -> str:
    """
    Check current platform/operating system where app is running

    Args:
        None

    Returns:
        Current platform (str): linux, OS X, win

    References:
        https://www.webucator.com/article/how-to-check-the-operating-system-with-python/
        https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
    """

    platforms: dict = {
        "linux1": "linux",
        "linux2": "linux",
        "darwin": "OS X",
        "win32": "win",
    }

    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


def provide_path_for_file(
    end_point: str, marker: str = None, status: str = None, method: str = None
) -> str:
    """

    Provide uniform format for file/folder path address

    Args:
        marker(str): currency, instrument, other
        end_point(str): orders, myTrades
        status(str): open, closed
        method(str): web/manual, api/bot

    Returns:
        Path address(str): in linux/windows format
    """
    from pathlib import Path

    current_os = get_platform()

    # Set root equal to  current folder
    root: str = Path(".")

    exchange = None

    if bool(
        [o for o in ["portfolio", 
                     "positions", 
                     "sub_accounts"
                     ] if (o in end_point)]
    ):
        exchange: str = "deribit"
        sub_folder: str = f"databases/exchanges/{exchange}/portfolio"

    if bool(
        [
            o
            for o in [
                "orders",
                "myTrades",'my_trades'
            ]
            if (o in end_point)
        ]
    ):
        exchange: str = "deribit"
        sub_folder: str = f"databases/exchanges/{exchange}/transactions"

    if bool(
        [
            o
            for o in [
                "ordBook",
                "index",
                "instruments",
                "currencies",
                "ohlc",
                "futures_analysis",
                "ticker-all",
                "ticker_all",
                "ticker",
            ]
            if (o in end_point)
        ]
    ):
        sub_folder = "databases/market"
        exchange = "deribit"

    if bool(
        [
            o
            for o in [
                "openInterestHistorical",
                "openInterestHistorical",
                "openInterestAggregated",
            ]
            if (o in end_point)
        ]
    ):
        sub_folder = "databases/market"
        exchange = "general"

    if marker != None:
        file_name = f"{marker.lower()}-{end_point}"

        if status != None:
            file_name = f"{file_name}-{status}"

        if method != None:
            file_name = f"{file_name}-{method}"

    else:
        file_name = f"{end_point}"

    if ".env" in end_point:
        sub_folder = "configuration"

    # to accomodate pytest env
    if "test.env" in end_point:
        sub_folder = "src/configuration"
        end_point = ".env"

    file_name = (f"{file_name}.pkl") if ".env" not in file_name else (f"{end_point}")

    # Combine root + folders
    my_path_linux: str = (
        root / sub_folder if exchange == None else root / sub_folder / exchange
    )
    my_path_win: str = (
        root / "src" / sub_folder
        if exchange == None
        else root / "src" / sub_folder / exchange
    )

    if "portfolio" in sub_folder or "transactions" in sub_folder:
        my_path_linux: str = (
            root / sub_folder if exchange == None else root / sub_folder
        )
        my_path_win: str = (
            root / "src" / sub_folder if exchange == None else root / "src" / sub_folder
        )

    # Create target Directory if it doesn't exist in linux
    if not os.path.exists(my_path_linux) and current_os == "linux":
        os.makedirs(my_path_linux)

    return (
        (my_path_linux / file_name)
        if get_platform() == "linux"
        else (my_path_win / file_name)
    )


def is_current_file_running(script: str) -> bool:
    """
    Check current file is running/not. Could be used to avoid execute an already running file

    Args:
        script (str): name of the file

    Returns:
        Bool: True, file is running

    References:
        https://stackoverflow.com/questions/788411/check-to-see-if-python-script-is-running
    """
    import psutil

    for q in psutil.process_iter():
        if q.name().startswith("python"):
            if (
                len(q.cmdline()) > 1
                and script in q.cmdline()[1]
                and q.pid != os.getpid()
            ):
                print("'{}' Process is already running".format(script))
                return True

    return False


def sleep_and_restart_program(idle: float = None) -> None:
    """

    Halt the program for some seconds and restart it

    Args:
        idle (float): seconds of the program halted before restarted.
        None: restart is not needed

    Returns:
        None

    """

    if idle != None:
        print(f" sleep for {idle} seconds")
        sleep(idle)

    print(f"restart")
    python = sys.executable
    os.execl(python, python, *sys.argv)

async def sleep_and_restart(idle: float = None) -> None:
    """

    Halt the program for some seconds and restart it

    Args:
        idle (float): seconds of the program halted before restarted.
        None: restart is not needed

    Returns:
        None

    """

    if idle != None:
        print(f" sleep for {idle} seconds")
        await asyncio.sleep(idle)

    print(f"restart")
    python = sys.executable
    os.execl(python, python, *sys.argv)

def catch_error_message(error: str, idle: float = None, message: str = None) -> None:
    """

    Capture & emit error message
    Optional: Send error message to telegram server

    Args:
        idle (float): seconds of the program halted before restarted. None: restart is not needed
        message (str): error message

    Returns:
        None

    Reference:
        https://medium.com/pipeline-a-data-engineering-resource/prettify-your-python-logs-with-loguru-a7630ef48d87

    """

    import traceback
    from utilities import telegram_app
    from loguru import logger as log

    info = f"{error} \n \n {traceback.format_exc()}"

    if message != None:
        info = f"{message} \n \n {error} \n \n {traceback.format_exc()}"

    if error == True:  # to respond 'def is_current_file_running'  result
        sys.exit(1)

    if error == "server rejected WebSocket connection: HTTP 503":
        log.critical(f"{error}")
        telegram_app.telegram_bot_sendtext(
            "server rejected WebSocket connection: HTTP 503"
        )

    log.critical(f"{error}")
    log.debug(traceback.format_exc())

    log.add(
        "error.log", backtrace=True, diagnose=True
    )  # Caution, may leak sensitive data in prod

    telegram_app.telegram_bot_sendtext(info)

    if idle != None:
        log.info(f"restart {idle} seconds after error")
        sleep_and_restart_program(idle)

    else:
        sys.exit()


def check_file_attributes(filepath: str) -> None:
    """

    Check file attributes

    Args:
        filepath (str): name of the file

    Returns:
        st_mode=Inode protection mode
        st_ino=Inode number
        st_dev=Device inode resides on
        st_nlink=Number of links to the inode
        st_uid=User id of the owner
        st_gid=Group id of the owner
        st_size=Size in bytes of a plain file; amount of data waiting on some special files
        st_atime=Time of last access
        st_mtime=Time of last modification
        st_ctime=
            Unix: is the time of the last metadata change
            Windows: is the creation time (see platform documentation for details).

    Reference:
        https://medium.com/@BetterEverything/automate-removal-of-old-files-in-python-2085381fdf51
    """
    return os.stat(filepath)
