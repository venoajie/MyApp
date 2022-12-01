#!/usr/bin/python3
# -*- coding: utf-8 -*-

from db_management import sqlite_operation

def create_dataBase_sqlite (db_name: str) -> None:

    '''
    '''    
     
    with sqlite_operation.db_ops() as cur:

        cur.execute("DROP TABLE IF EXISTS greeks") 
          
        
if __name__ == "__main__":
    
    try:   
        create_dataBase_sqlite()

    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except Exception as error:
        formula.log_error('database', 'main', error, 10)