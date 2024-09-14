import asyncio
from loguru import logger as log

import sqlite3

def backup_database(source_db, dest_db):
    log.error ("start")
    source_conn = sqlite3.connect(source_db)
    dest_conn = sqlite3.connect(dest_db)

    # Initialize the backup process
    backup = sqlite3.backup(source_conn, dest_conn)

    # Perform the backup
    backup.step(-1)

    # Finalize the backup
    backup.finish()

    # Close connections
    source_conn.close()
    dest_conn.close()

    log.error ("done")

# Example usage
source_db = "databases/trading.sqlite3"
dest_db = "databases/trading_bak.sqlite3"
backup_database(source_db, dest_db)