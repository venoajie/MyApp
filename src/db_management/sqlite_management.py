# # -*- coding: utf-8 -*-

import sqlite3
from contextlib import contextmanager
                                 
def catch_error (error, 
                 idle: int = None
                 ) -> list:
    """
    """
    from utilities import system_tools
    system_tools.catch_error_message(error, idle)


def telegram_bot_sendtext(bot_message: str, 
                          purpose: str
                          ) -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(
                                                bot_message, 
                                                purpose
                                                )

@contextmanager
def db_ops(db_name: str = 'trading.db')->None:

    '''
    # prepare sqlite initial connection + close
            Return and rtype: None
            #https://stackoverflow.com/questions/67436362/decorator-for-sqlite3/67436763#67436763
            # https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
            https://code-kamran.medium.com/python-convert-json-to-sqlite-d6fa8952a319
    ''' 
    
    try:
        conn = sqlite3.connect(db_name, isolation_level=None)
        cur = conn.cursor()
        yield cur
        
    except Exception as e:
            
        telegram_bot_sendtext('sqlite operation', 'failed_order')
        telegram_bot_sendtext(str(e), 'failed_order')
        print (e)
        conn.rollback()
        raise e

    else:        
        conn.commit()
        conn.close()

@contextmanager
def create_dataBase_sqlite(db_name: str = 'trading.db')->None:

    '''
    # prepare sqlite initial connection + close
            Return and rtype: None
            # https://stackoverflow.com/questions/67436362/decorator-for-sqlite3/67436763#67436763
            # https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
    ''' 
    
    conn = sqlite3.connect(db_name)
    conn.execute('BEGIN')            
    cur = conn.cursor()
    yield cur
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    
    try:   
        create_dataBase_sqlite()

    except (KeyboardInterrupt, SystemExit):
        catch_error (KeyboardInterrupt)

    except Exception as error:
        catch_error (error, 10)