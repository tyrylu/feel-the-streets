from .generator import Generator
from shared.models import Historic

class HistoricGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Historic)
        self.renames("historic", "type")
        self.renames("heritage:operator", "heritage_operator")
        self.removes("alt_name")

        self.renames("memorial:type", "memorial_type")
        self.renames("memorial:name", "memorial_name")
        self.renames("memorial:addr", "addr")
        self.renames("person:date_of_birth", "person_date_of_birth")
    @staticmethod
    def accepts(props):
        return "historic" in props and props["historic"] != "yes"
