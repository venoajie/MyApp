
def querying_based_on_currency_or_instrument_and_strategy (table: str, 
                                                           columns: list, 
                                                           item_limit,
                                                           limit: int, 
                                                           operator: str ) -> str:
    
    """_summary_
    
    status: all, open, closed

    Returns:
        _type_: _description_
    """
    standard_columns= (','.join(str(f"""{i}{("_dir as amount") if i=="amount" else ""}""") for i in columns))
        
    where_clause= f"WHERE ({item_limit} {operator} '%{limit}%')"

    tab = f"SELECT {standard_columns} FROM {table} {where_clause}"
    
    if limit > 0:
        
        tab= f"{tab} LIMIT {limit}"
    
    return tab
                                                 
column = f"data", "open_interest","tick"
print (f"""querying_based_on_currency_or_instrument_and_strategy {querying_based_on_currency_or_instrument_and_strategy ("ohlc1",   
       column,  "tick",5, "like")}""")