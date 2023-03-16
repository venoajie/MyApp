from utilities import number_modification


def test_is_floatable() -> bool:
    """ """
    its_float = 1.00
    assert number_modification.is_floatable(its_float) == True

    its_float = "1.00"
    assert number_modification.is_floatable(its_float) == True

    its_string = "Aa"
    assert number_modification.is_floatable(its_string) == False

    its_int = 1
    assert number_modification.is_floatable(its_int) == True


def test_convert_str_to_float_single() -> bool:
    """ """
    data_json = {"a": "1.0", "b": "2.0"}
    expected_result = [{"a": 1.0, "b": 2.0}]
    assert number_modification.convert_str_to_float_single(data_json) == expected_result

    data_json = [{"a": "1.0", "b": "2.0"}]

    expected_result = [{"a": 1.0, "b": 2.0}]

    assert number_modification.convert_str_to_float_single(data_json) == expected_result


def test_convert_str_to_float_single() -> bool:
    """ """
    data_json = [
        {"id": "1", "price": "2.3", "quantity": "4.5"},
        {"id": "2", "price": "3.4", "quantity": "5.6"},
    ]
    expected_result = [
        {"id": "1", "price": 2.3, "quantity": 4.5},
        {"id": "2", "price": 3.4, "quantity": 5.6},
    ]
    assert number_modification.convert_str_to_float(data_json) == expected_result


def test_get_nearest_tick():
    price1 = 1550.074
    price2 = 1550.52
    price3 = 1550.49

    tick = 0.05

    assert number_modification.get_nearest_tick(price1, tick) == 1550.05

    assert number_modification.get_nearest_tick(price2, tick) == 1550.5

    assert number_modification.get_nearest_tick(price3, tick) == 1550.45
