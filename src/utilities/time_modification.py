# -*- coding: utf-8 -*-

import calendar
from datetime import datetime, timedelta, timezone
import time


def get_current_local_date_time():
    """ """
    return datetime.now()


def translate_current_local_date_time_to_utc():
    """ """
    return (
        get_current_local_date_time()
        .astimezone()
        .astimezone(timezone.utc)
        .replace(tzinfo=None)
    )


def time_format_standardization(time_input, time_format: str = "%Y-%m-%d %H:%M:%S.%f"):
    """
    Standardize the time format.
    """
    # If the input is a string, then convert it to datetime format.
    strptime = (
        None
        if isinstance(time_input, str) == False
        else datetime.strptime(time_input, time_format)
    )

    # If the input is a datetime, then convert it to string format.
    strftime = (
        None
        if isinstance(time_input, datetime) == False
        else time_input.strftime(time_format)
    )

    # Return a dictionary with two keys: strptime and strftime.
    return {"strptime": strptime, "strftime": strftime}


def convert_time_to_utc(
    transaction_time: str = None, hours_diff_with_utc: float = None
):
    """
    # Mendapatkan waktu UTC/JKT saat ini (now) dengan UTC sebagai patokan

        Args:
            param (None): None

        Return and rtype:
            waktu utc/jkt dalam format yyyy/mm/dd --> dict

        Referensi:
            https://stackoverflow.com/questions/3327946/how-can-i-get-the-current-time-now-in-utc
    """

    utc = translate_current_local_date_time_to_utc()

    if transaction_time != None:
        transaction_time_ = datetime.fromisoformat(transaction_time)
        transaction_time = (
            transaction_time_.astimezone().astimezone(timezone.utc).replace(tzinfo=None)
        )
        utc_f_transaction_time = (
            transaction_time
            + timedelta(hours=0 if hours_diff_with_utc == None else hours_diff_with_utc)
        ).strftime("%Y-%m-%d %H:%M:%S.%f")

    utc_f = time_format_standardization(utc)["strftime"]
    utc_f_jkt = time_format_standardization((utc + timedelta(hours=7)))["strftime"]

    return {
        "utc_now": time_format_standardization(utc_f)["strptime"],
        "jkt_now": time_format_standardization(utc_f_jkt)["strptime"],
        "transaction_time": None
        if transaction_time == None
        else time_format_standardization(utc_f_transaction_time)["strptime"],
    }


def check_day_name(time: datetime) -> str:
    """
    check day name based on time given
    """
    # time in datetime format
    try:
        return time.strftime("%A")

    # time in text format
    except:
        # convert string to time format
        time_in_time_format = time_format_standardization(time)["strptime"]
        return time_in_time_format.strftime("%A")


def convert_time_to_unix(time) -> int:
    """
    # Get time  (milliseconds since the UNIX epoch)

        Args:
            param1 (Date): Waktu dalam format '%Y-%m-%d %H:%M:%S.%f'
            one minute = 60000

        Return and rtype:
            waktu dalam format UNIX (microseconds) utc/jkt --> int

        Referensi:
            https://stackoverflow.com/questions/41856393/time-data-conversion-missing-microseconds-in-gm-time-python
            https://stackoverflow.com/questions/10611328/parsing-datetime-strings-containing-nanoseconds
            https://stackoverflow.com/questions/58939822/python-does-not-match-format-y-m-dthmsz-f

    """

    try:
        try:
            time_ = 0 if time == 0 else datetime.fromisoformat(time)
            time = 0 if time == 0 else time_.strftime("%Y-%m-%d %H:%M:%S.%f")
            time = 0 if time == 0 else datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f")
            microsecs = time.microsecond

        except:
            microsecs = time.microsecond  # menarik microsecond untuk dihitung terpisah

    except Exception as error:
        import traceback
        from loguru import logger as log

        log.critical(f"{error}")
        print(traceback.format_exc())

    return int((calendar.timegm(time.timetuple()) * 1000000 + microsecs) / 1000)


def time_delta_between_now_and_transaction_time_both_in_utc(
    transaction_time: str,
) -> float:
    """Menghitung selisih  antara waktu saat ini dengan
    waktu saat transaksi

    """
    none_data = [None, 0, []]

    now_time_utc = convert_time_to_utc()["utc_now"]
    transaction_time_utc = convert_time_to_utc(transaction_time)["transaction_time"]

    # time_delta in seconds
    time_delta = (
        0
        if transaction_time in none_data
        else ((transaction_time_utc - now_time_utc).total_seconds())
    )

    return {
        "seconds": time_delta,
        "hours": time_delta / 3600,
        "days": time_delta / 3600 / 24,
    }


def time_delta_between_two_times(
    time_format, start_time: str, end_time: str = None
) -> float:
    """Menghitung selisih  antara waktu 2 waktu
    time format: utc/unix

    """
    # end time = now
    transaction_time_end_utc = convert_time_to_utc()["utc_now"]
    transaction_time_end_unix = convert_time_to_unix(transaction_time_end_utc)

    if time_format == "utc":
        if end_time != None:
            transaction_time_end_utc = convert_time_to_utc(end_time)["transaction_time"]
            transaction_time_end_unix = convert_time_to_unix(transaction_time_end_utc)

        transaction_time_start_utc = convert_time_to_utc(start_time)["transaction_time"]
        transaction_time_start_unix = convert_time_to_unix(transaction_time_start_utc)
        # transaction_time_end_utc = convert_time_to_utc (end_time)['transaction_time']

        # time_delta in seconds
        time_delta_utc = (
            transaction_time_end_utc - transaction_time_start_utc
        ).total_seconds()
        time_delta_unix = transaction_time_end_unix - transaction_time_start_unix

    if "unix" in time_format:
        seconds_divider = 1000 if "ms" in time_format else 1000
        transaction_time_end_unix = (
            transaction_time_end_unix if end_time == None else end_time
        )

        # time_delta in seconds
        time_delta_unix = transaction_time_end_unix - start_time

    return {
        "seconds": time_delta_unix / seconds_divider
        if "unix" in time_format
        else time_delta_utc,
        "hours": time_delta_unix / 3600 / seconds_divider
        if "unix" in time_format
        else time_delta_utc / 3600,
        "days": time_delta_unix / 3600 / seconds_divider / 24
        if "unix" in time_format
        else time_delta_utc / 3600 / 24,
    }


def check_alarm_clock(
    triggerHour, triggerMinute, isTrigger=False, local_time: str = None
):
    """

    Add an alarm clock to the trading strategy

    Args:
        triggerHour (int)
        triggerMinute (int)

    Returns:
        str

    Example:
        data_original = 'hedgingSpot-open-1671189554374' become 'hedgingSpot'

    Reference:
        https://medium.com/@FMZQuant/add-an-alarm-clock-to-the-trading-strategy-e90e0372405f
    """

    if local_time == "jkt_now":
        current_time = convert_time_to_utc()["jkt_now"]
    else:
        current_time = convert_time_to_utc()["utc_now"]

    t = time.localtime(time.time())
    hour = t.tm_hour
    minute = t.tm_min
    day = t.tm_wday

    nowDay = time.localtime(time.time()).tm_wday

    if day != nowDay:
        isTrigger = False
        nowDay = day

    if isTrigger == False and hour == triggerHour and minute >= triggerMinute:
        isTrigger = True
        return True

    return False
