import pint
from .di import Singleton

def create_ereg():
    from .entity_registry import EntityRegistry
    return EntityRegistry()

unit_registry = Singleton(pint.UnitRegistry)
entity_registry = Singleton(factory=create_ereg)