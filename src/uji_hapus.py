
import tomli
  
  
# Opening a Toml file using tomlib 
with open("home/live/MyApp/src/strategies/config_strategies.toml","rb") as toml: 
    toml_dict = tomli.load(toml) 
  
# Printing the entire fetched toml file 
print(toml_dict)