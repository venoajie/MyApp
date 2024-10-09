from abc import ABC, abstractmethod
from dataclassy import dataclass

# Abstract Product Classes
@dataclass
class Chair(ABC):

    @abstractmethod
    def sit_on(self):
        pass

@dataclass
class Sofa(ABC):

    @abstractmethod
    def lie_on(self):
        pass

@dataclass
class Table(ABC):

    @abstractmethod
    def put_stuff_on(self):
        pass

# Concrete Product Classes
@dataclass
class ModernChair(Chair):

    def sit_on(self):
        return "Sitting on a modern chair."

@dataclass
class ModernSofa(Sofa):

    def lie_on(self):
        return "Lying on a modern sofa."

@dataclass
class ModernTable(Table):

    def put_stuff_on(self):
        return "Putting stuff on a modern table."

# Abstract Factory Class
@dataclass
class FurnitureFactory(ABC):

    @abstractmethod
    def create_chair(self):
        pass

    @abstractmethod
    def create_sofa(self):
        pass

    @abstractmethod
    def create_table(self):
        pass

# Concrete Factory Classes
@dataclass
class ModernFurnitureFactory(FurnitureFactory):

    def create_chair(self):
        return ModernChair()

    def create_sofa(self):
        return ModernSofa()

    def create_table(self):
        return ModernTable()

# Client Code
@dataclass
def furnish_room(factory):
    chair = factory.create_chair()
    sofa = factory.create_sofa()
    table = factory.create_table()
    print(chair.sit_on())
    print(sofa.lie_on())
    print(table.put_stuff_on())

# Usage
modern_factory = ModernFurnitureFactory()
furnish_room(modern_factory)