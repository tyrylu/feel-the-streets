from . import Named, Address

class Theatre(Named):
    address: Address = None
    is_in: str = None
    levels: int = None
    flats: int = None