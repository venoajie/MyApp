from db_management import sqlite_management

def perform_query_from_sqlite (table: str)->list:

    '''
            Reference
            # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
    ''' 

    query_table = f'SELECT * FROM {table}' 
    
    with sqlite_management.db_ops() as cur:
        try:
#            log.warning (query_table)
            result = (list(cur.execute((f'{query_table}')))) 
#            log.warning (result)
            
            headers = list(map(lambda attr : attr[0], cur.description))
#            log.debug (headers)
                        
            combine_result = []
            for i in result:
                combine_result.append(dict(zip(headers,i)))
                
        except Exception as error:
            from utils import formula
            from db_management import insert_strategy_entries_to_sqlite
            
            insert_strategy_entries_to_sqlite.create_table_strategy()

            formula.log_error('execute strategy_entries', 'fetch_open_strategies', error, 30)    

        return [] if (combine_result ==[] or  combine_result == None ) else  (combine_result)

                
def querying_strategies_sent (table: str = 'strategy_entries')->list:

    '''
            Reference
            # https://stackoverflow.com/questions/65934371/return-data-from-sqlite-with-headers-python3
    ''' 
    query_table = f'SELECT  * FROM {table} WHERE  strategyStatus = ?' 
    params = ('sent')
    
    try:
        with sqlite_management.db_ops() as cur:
            result = list(cur.execute((f'{query_table},{params}')))
            headers = list(map(lambda attr : attr[0], cur.description))
                        
            combine_result = []
            for i in result:
                combine_result.append(dict(zip(headers,i)))
                
    except Exception as error:
        from utils import formula
        formula.log_error('app','name-try2', error, 10)
        combine_result = []
        
        return 0 if (combine_result ==[] or  combine_result == None ) else  (combine_result)


def query_pd ():
    """
    # fetch tickers from sqlite3 by pandas and transform them to dict
    # https://medium.com/@sayahfares19/making-pandas-fly-6-pandas-best-practices-to-save-memory-energy-8d09e9d52488
    # https://pythonspeed.com/articles/pandas-sql-chunking/
    """
    import pandas as pd
    import sqlite3
            
    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect('trading')
    
    #fetch all
    result = pd.read_sql_query("SELECT * from strategy_entries", con)         
    
    #transform dataframe to dict
    result = result.to_dict('records')

    #close connection sqlite
    con.close()     

    return  result