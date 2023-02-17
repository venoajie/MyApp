#!/usr/bin/python3
import psycopg2.extras
from psycopg2 import connect, sql
import contextlib


class Postgresql:
    """Menyiapkan koneksi ke exchange, database, telegram, atau aplikasi lainnya"""

    def __init__(self):
        self.params = None
        self.conn = None
        
    @contextlib.contextmanager
    def open_connection_to_postgre(
                                    self,
                                    params
                                    ):
        """Connect to a Postgres database
        https://towardsdatascience.com/python-context-managers-in-10-minutes-using-the-with-keyword-51eb254c1b89
        ."""

        if self.conn is None:
            print("Connecting to PostgreSQL database...")
            
            try:
               
                self.conn = psycopg2.connect(**params)
                
                cur = self.conn.cursor()
                try:
                    yield cur
                finally:
                    # Teardown script
                    cur.close()
                    self.conn.close()
                    print("Database connection closed.")
        
                print(f'{self.conn=}')

            # bila terdapat error terkait koneksi ke postgres         
            except psycopg2.DatabaseError as e:
                raise e
                
        return self.conn


    def create_db(self,
                  params,
                  db_name: str = 'tradingdb'
                  ):
        """Create a Postgres database."""

    
        try:
            
            conn = self.open_connection_to_postgre(params)
            conn.autocommit = True

            # Creating a cursor object
            cursor = conn.cursor()
            
            # query to create a database
            sql = f''' CREATE database {db_name} '''
            
            # executing above query
            cursor.execute(sql)
            print("Database has been created successfully !!")
            
            # Closing the connection
            conn.close()

        except psycopg2.DatabaseError as e:
            raise e
        finally:
            print('Koneksi ke database terbuka')
        return self.conn


if __name__ == "__main__":

    try:
        Psql = Postgresql ()

        db_params = dict(
            host="localhost", database="tradingdb", user="postgres", password="Abcd1234"
        )
        with Psql.open_connection_to_postgre(db_params) as db_conn:
            data = db_conn.execute("SELECT * FROM table")
            print (data)
            
    except (KeyboardInterrupt):
        catch_error (KeyboardInterrupt)

    except Exception as error:
        print (error, 30)
