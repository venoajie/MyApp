from abc import ABC, abstractmethod,ABCMeta
from dataclasses import dataclass
import asyncio
#from dataclassy import dataclass
# Abstract Product Classes


@dataclass
class ManageStrategy (metaclass=ABCMeta):
    """ """

    @abstractmethod
    async def opening_position (self) -> None:
        """ """
        pass
    

    @abstractmethod
    async def closing_position (self) -> None:
        """ """
        pass
    

    @abstractmethod
    async def risk_managament (self) -> None:
        """ """
        pass
    

    @abstractmethod
    async def cancelling_order (self) -> None:
        """ """
        pass
    

    @abstractmethod
    async def edit_order (self) -> None:
        """ """
        pass

@dataclass
class BasicStrategy (ManageStrategy):
    """ """

    def opening_position (self) -> None:
        """ """
        pass
    

    def closing_position (self) -> None:
        """ """
        pass
    

    def risk_managament (self) -> None:
        """ """
        pass
    

    def cancelling_order (self) -> None:
        """ """
        pass
    

    def edit_order (self) -> None:
        """ """
        pass
    
    def get_basic_opening_parameters(self) -> dict:
        """ """

        # provide placeholder for params
        print ("AAAAAAAAAAAAAAAAAAAAAAAAAAA")
basic_strategy= BasicStrategy()
basic_strategy.get_basic_opening_parameters()