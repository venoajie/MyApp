#!/usr/bin/python3
import psycopg2.extras
from psycopg2 import connect, sql


class Postgresql:
    """Menyiapkan koneksi ke exchange, database, telegram, atau aplikasi lainnya"""

    def __init__(self):
        self.params = None
        self.conn = None
        
    def open_connection_to_postgre(self,
                                   params
                                   ):
        """Connect to a Postgres database."""

        if self.conn is None:
            try:
               
                self.conn = psycopg2.connect(**params)
#                print(f'{self.conn=}')

            # bila terdapat error terkait koneksi ke postgres         
            except psycopg2.DatabaseError as e:
                raise e
            finally:
                print('Koneksi ke database terbuka')
        return self.conn



if __name__ == "__main__":

    try:
        
        asyncio.get_event_loop().run_until_complete(main())
        
        # only one file is allowed to running
        is_running = system_tools.is_current_file_running ('apply_strategies.py')
        
        if is_running:
            catch_error (is_running)
        
        system_tools.sleep_and_restart_program (30)

    except (KeyboardInterrupt):
        catch_error (KeyboardInterrupt)

    except Exception as error:
        catch_error (error, 30)
