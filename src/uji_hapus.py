
import tomlli
  
  
# Opening a Toml file using tomlib 
with open("src/strategies/config_strategies.toml","rb") as toml: 
    toml_dict = tomlli.load(toml) 
  
# Printing the entire fetched toml file 
print(toml_dict)