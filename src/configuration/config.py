# -*- coding: utf-8 -*-

from configparser import ConfigParser
from loguru import logger as log

def catch_error (error, idle: int = None) -> list:
    """
    """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)

class Read_Configuration:
    """Menyiapkan koneksi ke exchange, database, telegram, atau aplikasi lainnya"""

    def __init__(self):
        self.params = None
        self.conn = None
        
    def config(self, 
               filename: str, 
               section: str
               )-> dict: 
        
        # buat parser 
        parser = ConfigParser() 
        log.error(parser.read(filename) )

        # baca file config  
        parser.read(filename) 

        # siapkan tempat untuk hasil bacaan file config  
        parameters = {} 

        if self.params is None:

        # detailkan parameters berdasarkan seksi
            if parser.has_section(section): 
                params = parser.items(section) 
                for param in params: 
                    parameters[param[0]] = param[1] 

        # bila seksi yang dicari tidak ada
            else: 
                raise Exception('Section {0} not found in the {1} file'.format(section, filename)) 
    
        log.warning (parameters)
        return parameters

def main_dotenv (header: str
          ):
    
    '''
    # Menyiapkan kredensial exchange dan akun/sub akun
            Return and rtype: kredensial (str)
    '''    

    filename = "src/configuration/.env"  # ? Mengakses file konfigurasi (api)
    Connection = Read_Configuration ()  # ? Menyiapkan koneksi ke masing-masing exchange
    
    return Connection.config (filename,
                              header
                              )

    
if __name__ == "__main__":

    try:
        
        main_dotenv ('deribit')
        
    except (KeyboardInterrupt):
        catch_error (KeyboardInterrupt)

    except Exception as error:
        catch_error (error, 30)
