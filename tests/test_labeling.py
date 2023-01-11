#from configuration import label_numbering
from src.configuration import label_numbering
from src.utilities import time_modification

def test_label_numbering  ():
        
    strategy = 'hedging spot'
    
    now_utc = time_modification.convert_time_to_utc () ['utc_now']
    now_unix = time_modification.convert_time_to_unix (now_utc)
    # close position
    assert label_numbering.labelling ('close',strategy, 'hedging spot-close-1671032009858') == 'hedging spot-close-1671032009858'
    # open position. rounding unix time to last 2 figures
    assert label_numbering.labelling ('open',strategy)[:29] == f'hedging spot-open-{now_unix}'[:29]
