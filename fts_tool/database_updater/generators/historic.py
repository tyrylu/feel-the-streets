from .generator import Generator
from shared.models import Historic

class HistoricGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Historic)
        self.renames("historic", "type")
        self.renames("heritage:operator", "heritage_operator")
        self.removes("alt_name")

    @staticmethod
    def accepts(props):
        return "historic" in props and props["historic"] != "yes"