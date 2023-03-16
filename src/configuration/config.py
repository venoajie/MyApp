# -*- coding: utf-8 -*-

from configparser import ConfigParser
from loguru import logger as log
from utilities import system_tools


def catch_error(error, idle: int = None) -> list:
    """ """
    from utilities import system_tools

    system_tools.catch_error_message(error, idle)


class Read_Configuration:

    """
    # Read .env file
    """

    def __init__(self):
        self.params = None
        self.conn = None

    def config(self, filename: str, section: str) -> dict:
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
                raise Exception(
                    "Section {0} not found in the {1} file".format(section, filename)
                )

        return parameters


def main_dotenv(header: str = "None", filename: str = ".env") -> dict:
    """
    https://www.python-engineer.com/posts/run-python-github-actions/
    """

    # Initialize credentials to None
    credentials = None

    try:
        # Set the filename
        # filename = ".env"
        config_path = system_tools.provide_path_for_file(filename)

        # Create a Read_Configuration object
        Connection = Read_Configuration()

        credentials = Connection.config(config_path, header)

    # to accomodate transition phase. Will be deleted
    except:
        import os
        from os.path import join, dirname
        from dotenv import load_dotenv

        dotenv_path = join(dirname(__file__), ".env")
        load_dotenv(dotenv_path)

        # github env
        credentials = os.environ
        # log.info (credentials)

    return credentials


if __name__ == "__main__":
    try:
        test = main_dotenv("telegram-failed_order")
        print(test)

        test = main_dotenv("deribit-147691")
        print(test)

    except KeyboardInterrupt:
        catch_error(KeyboardInterrupt)

    except Exception as error:
        catch_error(error, 30)
