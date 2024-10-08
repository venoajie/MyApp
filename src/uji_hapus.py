
from websocket_management.ws_management import (
    get_config)                

file_toml = "config_strategies.toml"
    
config_app =[o for o in get_config(file_toml) ["strategies"] if o["strategy_label"]=="hedgingSpot"] 

print (config_app)
