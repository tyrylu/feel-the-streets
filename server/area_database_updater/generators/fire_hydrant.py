from .generator import Generator
from shared.entities import FireHydrant

class FireHydrantGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(FireHydrant)
        self.unprefixes("fire_hydrant")

    @staticmethod
    def accepts(props):
        return "fire_hydrant:type" in props or ("emergency" in props and props["emergency"] == "fire_hydrant")