# # -*- coding: utf-8 -*-

import sqlite3
from contextlib import contextmanager

def telegram_bot_sendtext(bot_message, purpose) -> None:
    from utils import telegram_app
    return telegram_app.telegram_bot_sendtext(bot_message, purpose)

@contextmanager
def db_ops(db_name: str = 'trading.db')->None:

    '''
    # prepare sqlite initial connection + close
            Return and rtype: None
            #https://stackoverflow.com/questions/67436362/decorator-for-sqlite3/67436763#67436763
            # https://charlesleifer.com/blog/going-fast-with-sqlite-and-python/
    ''' 

    #conn.execute('BEGIN')
    
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
        db_ops()

    except (KeyboardInterrupt, SystemExit):
        sys.exit()

    except Exception as error:
        formula.log_error('database', 'main', error, 10)