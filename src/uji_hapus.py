
from websocket_management.ws_management import (get_config)


file_toml = "config_strategies.toml"
    
config_app = get_config(file_toml)

strategies_config_app = config_app["strategies"]

weighted_factor= [o["weighted_factor"] for o in strategies_config_app if "hedgingSpot" in o["strategy_label"]]
print (f"weighted_factor {weighted_factor}")
waiting_minute_before_cancel= [o["waiting_minute_before_cancel"] for o in strategies_config_app if "hedgingSpot" in o["strategy_label"]]
