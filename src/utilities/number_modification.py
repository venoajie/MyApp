# -*- coding: utf-8 -*-


def is_floatable(num: any) -> bool:
    """
    https://www.programiz.com/python-programming/examples/check-string-number
    """
    if num == None:
        return None

    else:
        try:
            float(num)
            return True
        except ValueError:
            return False


def convert_str_to_float_single(data_json: list) -> list:
    """
    https://stackoverflow.com/questions/21193682/convert-a-string-key-to-int-in-a-dictionary
            Return and rtype:
            Catatan:
    """

    if isinstance(data_json, dict):
        return [
            {k: float(eval(v)) if is_floatable(v) else v for k, v in data_json.items()}
        ]
    if isinstance(data_json, list):
        data_json = data_json[0]
        return [{k: float(v) if is_floatable(v) else v for k, v in data_json.items()}]


def convert_str_to_float(data_json: list) -> object:
    """
    https://stackoverflow.com/questions/21193682/convert-a-string-key-to-int-in-a-dictionary
            Return and rtype:
            Catatan:
    """
    excluded = [
        "id",
        "reduceOnly",
        "postOnly",
        "liquidation",
        "ioc",
        "market",
        "future",
        "type",
        "side",
        "orderId",
        "time",
        "tradeId",
        "feeCurrency",
        "liquidity",
        "baseCurrency",
        "quoteCurrency",
        "coin",
    ]

    if isinstance(data_json, dict):
        data_json = [data_json]

    if len(data_json) == 1:
        # data_json=data_json[0]
        return convert_str_to_float_single(data_json)

    if len(data_json) > 1:
        list_combination = []
        for i in data_json:
            if isinstance(i, dict):
                data_json = [data_json]
                position = {
                    k: float(v) if (is_floatable(v) and (k) not in excluded) else v
                    for k, v in i.items()
                }
            if isinstance(i, list):
                position = {
                    k: float(v) if (is_floatable(v) and (k) not in excluded) else v
                    for k, v in i.items()
                }
            list_combination.append(position)

        return list_combination


def presisi_pembulatan(angka):
    """
    # Menghitung berapa angka di belakang koma untuk keperluan pembulatan

        Args:
            param1 (float): yang ingin dibulatkan (float: 0.xx atau 1e4)

        Return and rtype:
            berapa angka di belakang koma --> int

        Referensi:
            https://stackoverflow.com/questions/38847690/convert-float-to-string-in-positional-format-without-scientific-notation-and-fa
            https://stackoverflow.com/questions/3886402/how-to-get-numbers-after-decimal-point
            https://stackoverflow.com/questions/26231755/count-decimal-places-in-a-float
    """

    from numpy import format_float_positional as format_float

    angka = str(format_float(angka))

    return int(angka[::-1].find("."))


def rounding(variable, TICK, presisi):
    """
    # Pembulatan berdasarkan tick per instrumen agar sesuai dengan standar harga exchange

        Args:
            param1 (float): angka yang akan dibulatkan
            param2 (float): tick angka
            param3 (int): presisi hasil pembulatan

        Return and rtype:
            hasil pembulatan --> float

    """
    rounding = int(variable / TICK)
    rounding = float(round(rounding * TICK, presisi))

    return rounding


def net_position(selected_transactions: list) -> float:
    """
    net sell: negative, net buy: positive

    """

    if selected_transactions != []:
        try:
            sum_sell = sum(
                [o["amount"] for o in selected_transactions if o["direction"] == "sell"]
            )  # sell = + sign
            sum_buy = sum(
                [o["amount"] for o in selected_transactions if o["direction"] == "buy"]
            )

            #! -1 + 1 = 0, -10+10 = 0, [] = 0, None = 0. [] = No transcations, diff with net = 0 (could affect to leverage)
            #! solution = made another controls for leverage/modify output/preventive
            return sum_buy - sum_sell

        except:
            return ([o["size"] for o in selected_transactions])[0]  # sell = (-) sign

    else:
        return selected_transactions


def get_nearest_tick(price: float, tick: float) -> float:
    """ """
    len_tick = len(str(tick)) - 2

    return round((int(price / tick)) * tick, len_tick)
