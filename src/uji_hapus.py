from strategies.entries_exits import strategies,hedging_spot_attributes
from utilities.string_modification import remove_redundant_elements, remove_double_brackets_in_list


def get_instruments_settlement_period () -> list:
    
    return (remove_redundant_elements(remove_double_brackets_in_list([o["settlement_period"]for o in (strategies+hedging_spot_attributes())])))
    
print(get_instruments_settlement_period())