# -*- coding: utf-8 -*-

from configparser import ConfigParser

def catch_error (error,
                 idle: int = None
                 ) -> list:
    """
    """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)

class Read_Configuration:

    '''
    # Read .env file
    '''    
    def __init__(self):
        self.params = None
        self.conn = None
        
    def config(self, 
               filename: str, 
               section: str
               )-> dict: 
        
        # create parser 
        parser = ConfigParser() 

        # read file config  
        parser.read(filename) 

        # prepare place holder for file config read result 
        parameters = {} 

        if self.params is None:

        # check file section
            if parser.has_section(section): 
                params = parser.items(section) 
                for param in params: 
                    parameters[param[0]] = param[1] 

        # if section is not provided
            else: 
                raise Exception('Section {0} not found in the {1} file'.format(section, filename)) 
    
        return parameters

def main_dotenv (header: str = 'None')-> dict:    
    
    """
    https://www.python-engineer.com/posts/run-python-github-actions/
    """
    from loguru import logger as log
    # Initialize credentials to None
    credentials = None 
    
            
    try: 
            
        # Set the filename
        filename = "src/configuration/.env" 
        
        # Create a Read_Configuration object
        Connection = Read_Configuration () 
        log.warning (header)
        
        credentials =  Connection.config (filename,
                                          header
                                          )
        log.warning (credentials)

    # github env
    except Exception as error:
        
        log.warning (error)
        log.warning (header)
        import os
        from os.path import join, dirname
        from dotenv import load_dotenv
        
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        
        # github env
        credentials = os.environ
        log.warning (credentials)
            
    return credentials
                          

if __name__ == "__main__":

    try:
        
        test = main_dotenv ('telegram-failed_order')
        print (test)
        
        test = main_dotenv ('deribit-147691')
        print (test)
        
    except (KeyboardInterrupt):
        catch_error (KeyboardInterrupt)

    except Exception as error:
        catch_error (error, 30)
