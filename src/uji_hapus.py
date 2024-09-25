
import tomli
from utilities.system_tools import provide_path_for_file  
  
# Opening a Toml file using tomlib 
with open(provide_path_for_file("config_strategies.toml"),"rb") as toml: 
    toml_dict = tomli.load(toml) 
  
# Printing the entire fetched toml file 
print(toml_dict)