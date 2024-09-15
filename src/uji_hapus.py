from loguru import logger as log

from utilities.system_tools import (
    catch_error_message)
import sqlite3

def progress(status, remaining, total):
    log.warning(f'Copied {total-remaining} of {total} pages...')
    
def back_up_db():
    src = sqlite3.connect("databases/trading.sqlite3")
    dst = sqlite3.connect("databases/trading.bak")
    with dst:
        src.backup(dst)
    dst.close()
    src.close()

    catch_error_message(
    "back up done")

        
if __name__ == "__main__":
    
    back_up_db()
    