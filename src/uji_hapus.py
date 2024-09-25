
import tomli
  
  
# Opening a Toml file using tomlib 
with open("./strategies/config_strategies.py","rb") as toml: 
    toml_dict = tomli.load(toml) 
  
# Printing the entire fetched toml file 
print(toml_dict)