
import tomli,os
from utilities.system_tools import provide_path_for_file 
from utilities.pickling import read_data 
from strategies import config_strategies
# Opening a Toml file using tomlib 
with open(provide_path_for_file("config_strategies.toml"),"rb") as toml: 
    toml_dict = tomli.load(toml) 

def get_trading_config(file_name: str) -> list:
    """ """
    config_path = provide_path_for_file (file_name)

    try:
        if os.path.exists(config_path):
            with open(config_path, "rb") as handle:
                read= tomli.load(handle)
                return read
    except:
        return []

  
# Printing the entire fetched toml file 
config_path=provide_path_for_file ("config_strategies.toml")
print(get_trading_config("config_strategies.toml"))