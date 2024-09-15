from loguru import logger as log

from utilities.system_tools import (
    catch_error_message)
import sqlite3

from configuration.config import main_dotenv

def parse_dotenv(sub_account) -> dict:
    return main_dotenv(sub_account)

        
async def get_private_data() -> list:
    """
    Provide class object to access private get API
    """

    sub_account = "backblaze-backup-trading-sqlite"
    client_id: str = parse_dotenv(sub_account)["client_id"]
    client_secret: str = parse_dotenv(sub_account)["client_secret"]
    return 

        
if __name__ == "__main__":
    
    back_up_db()
    