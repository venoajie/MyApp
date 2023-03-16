from src.configuration import label_numbering
from src.utilities import time_modification

strategy = "hedgingSpot"


def test_labelling():
    # labelling_without_id_strategy
    # close position
    assert (
        label_numbering.labelling("close", strategy, "hedgingSpot-close-1671032009858")
        == "hedgingSpot-close-1671032009858"
    )

    now_utc = time_modification.convert_time_to_utc()["utc_now"]
    now_unix = time_modification.convert_time_to_unix(now_utc)
    # labelling_with_id_strategy
    # open position. rounding unix time to last 2 figures
    assert (
        label_numbering.labelling("open", strategy)[:27]
        == f"hedgingSpot-open-{now_unix}"[:27]
    )
