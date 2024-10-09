from abc import ABC, abstractmethod,ABCMeta
from dataclassy import dataclass

# Abstract Product Classes

@dataclass(unsafe_hash=True, slots=True)
class DatabaseConnection:
    def connect(self):
        pass

# Concrete Product Classes for MySQL
@dataclass(unsafe_hash=True, slots=True)
class MySQLConnection(DatabaseConnection):

    def connect(self):
        return "Connecting to MySQL database"

# Concrete Product Classes for PostgreSQL
@dataclass(unsafe_hash=True, slots=True)
class PostgreSQLConnection(DatabaseConnection):

    def connect(self):
        return "Connecting to PostgreSQL database"

# Abstract Factory Class
@dataclass(unsafe_hash=True, slots=True)
class DatabaseConnectionFactory:

    def create_connection(self):
        pass

# Concrete Factory Classes
@dataclass(unsafe_hash=True, slots=True)
class MySQLConnectionFactory(DatabaseConnectionFactory):

    def create_connection(self):
        return MySQLConnection()

@dataclass(unsafe_hash=True, slots=True)
class PostgreSQLConnectionFactory(DatabaseConnectionFactory):

    def create_connection(self):
        return PostgreSQLConnection()

# Client Code
def connect_to_database(factory):
    connection = factory.create_connection()
    print(connection.connect())

# Usage
mysql_factory = MySQLConnectionFactory()
connect_to_database(mysql_factory)
postgresql_factory = PostgreSQLConnectionFactory()
connect_to_database(postgresql_factory)