from abc import ABC, abstractmethod

# Abstract Product Classes
class Chair(ABC):

    @abstractmethod
    def sit_on(self):
        pass

class Sofa(ABC):

    @abstractmethod
    def lie_on(self):
        pass

class Table(ABC):

    @abstractmethod
    def put_stuff_on(self):
        pass

# Concrete Product Classes
class ModernChair(Chair):

    def sit_on(self):
        return "Sitting on a modern chair."

class ModernSofa(Sofa):

    def lie_on(self):
        return "Lying on a modern sofa."

class ModernTable(Table):

    def put_stuff_on(self):
        return "Putting stuff on a modern table."

class VintageChair(Chair):

    def sit_on(self):
        return "Sitting on a vintage chair."

class VintageSofa(Sofa):

    def lie_on(self):
        return "Lying on a vintage sofa."

class VintageTable(Table):

    def put_stuff_on(self):
        return "Putting stuff on a vintage table."

# Abstract Factory Class
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
class ModernFurnitureFactory(FurnitureFactory):

    def create_chair(self):
        return ModernChair()

    def create_sofa(self):
        return ModernSofa()

    def create_table(self):
        return ModernTable()

class VintageFurnitureFactory(FurnitureFactory):

    def create_chair(self):
        return VintageChair()

    def create_sofa(self):
        return VintageSofa()

    def create_table(self):
        return VintageTable()

# Client Code
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
vintage_factory = VintageFurnitureFactory()
furnish_room(vintage_factory)