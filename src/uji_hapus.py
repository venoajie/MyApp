import asyncio
from loguru import logger as log

import sqlite3

def progress(status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')

src = sqlite3.connect("databases/trading.sqlite3")
dst = sqlite3.connect("databases/trading3.sqlite3")
with dst:
    src.backup(dst, pages=1, progress=progress)
dst.close()
src.close()

def backup_database(source_db, dest_db):
    log.error ("start")
    source_conn = sqlite3.connect(source_db)
    dest_conn = sqlite3.connect(dest_db)

    # Initialize the backup process
    backup = source_conn.backup(source_conn, dest_conn)

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