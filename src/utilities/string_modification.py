# -*- coding: utf-8 -*-


def remove_redundant_elements(data: list) -> list:
    """
    Remove redundant items in a list

    Args:
        data (list)

    Returns:
        list:

    Example:
        data_original = ['A', 'A', 'B', 'B', 'B', 'C']
        data_cleaned = ['A','B','C']

    Reference:
        1. https://stackoverflow.com/questions/9427163/remove-duplicate-dict-in-list-in-python
        2. https://python.plainenglish.io/how-to-remove-duplicate-elements-from-lists-without-using-sets-in-python-5796e93e6d43
    """

    # Create an empty list
    result = []

    # Check if the data is a list and not empty
    if isinstance(data, list) and data != []:
        try:
            # Ref 1
            result = list({frozenset(item.items()): item for item in data}.values())

        except:
            # Ref 2
            result = list(dict.fromkeys(data))

    return result


def find_unique_elements(data1: list, data2: list) -> list:
    """

    Comparing two lists and picking only unique items between them

    Args:
        data (list)  and its subset (list) for comparation

    Returns:
        list

    Example:
        data_original = [1, 2, 3, 4, 5] # all data
        data_redundant = [2, 4] # subset of all data
        data_cleaned =  [1, 3, 5]

    Reference:
        https://stackoverflow.com/questions/45098206/unique-values-between-2-lists

    """
    return [i for i in data1 if i not in data2]


def extract_currency_from_text(words: str) -> str:
    """
    Extracting currency from channel message
    """

    if "eth" in (words).lower():
        return "eth"
    if "btc" in (words).lower():
        return "btc"

def extract_integers_from_text(words: list) -> int:
    """
    Extracting integers from label text
    """

    try:
        return int("".join([o for o in words if o.isdigit()]))

    except:
        return []


def parsing_sqlite_json_output (json_load: list) -> int:
    """
    parsing_sqlite_json_output
    
    References:
        https://stackoverflow.com/questions/46991650/remove-quotes-from-list-of-dictionaries-in-python
        https://stackoverflow.com/questions/14611352/malformed-string-valueerror-ast-literal-eval-with-string-representation-of-tup
    """
    import ast

    try:
                
        result_json =  [i.replace(':false', ':False').replace(':true', ':True') .replace(':null', ':None') for i in json_load] 
        return ([ast.literal_eval(str(i)) for i in result_json])

    except:
        return []

def get_strings_before_character(
    label: str, character: str = "-", 
    character_place: int = [0, 2]
) -> str:
    """

    Get strings before a character

    Args:
        label (str)
        character (str)
        character_place (list (default)/int)

    Returns:
        str

    Example:
        data_original = 'hedgingSpot-open-1671189554374' become 'hedgingSpot'

    Reference:
        https://stackoverflow.com/questions/32682199/how-to-get-string-before-hyphen
    """

    if isinstance(character_place, list):
        splitted1 = label.split(character)[character_place[0]]
        splitted2 = label.split(character)[character_place[1]]
        splitted = f"{splitted1}-{splitted2}"
    else:
        splitted = label.split(character)[character_place]

    return splitted


def parsing_label(label: str) -> str:

    """


    Args:
        label (str)
        level (str)

    Returns:
        str

    Example: 'hedgingSpot-open-1671189554374'
        main: 'hedgingSpot'
        int = 1671189554374
        transaction_status:'hedgingSpot-open''
        transaction_net:'hedgingSpot-1671189554374''

    """
    try:
        get_integer = get_strings_before_character (label, "-", 2)
    except:
        get_integer = None

    try:
        status = get_strings_before_character (label, "-", [0, 1])
    except:
        status = None

    try:
        net =  get_strings_before_character (label)
    except:
        net = None

    return  {
        "main": get_strings_before_character (label, "-", 0),
        "int": get_integer,
        "transaction_status": status,
        "transaction_net": net
        }
