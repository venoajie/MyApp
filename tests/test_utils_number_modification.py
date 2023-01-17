from utilities import number_modification

def test_get_nearest_tick  ():
    price1 =1550.074
    price2 =1550.52
    price3 =1550.49
    
    tick =  0.05
    
    assert number_modification.get_nearest_tick (price1, tick) == 1550.05
    assert number_modification.get_nearest_tick (price2, tick) == 1550.5
    assert number_modification.get_nearest_tick (price3, tick) == 1550.45