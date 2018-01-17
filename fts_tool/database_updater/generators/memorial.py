from .historic import HistoricGenerator
from shared.models import Memorial

class MemorialGenerator(HistoricGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Memorial)
        self.renames("memorial:type", "memorial_type")
        self.renames("memorial", "memorial_kind")
        self.renames("heritage:operator", "heritage_operator")
        self.renames("person:date_of_birth", "person_date_of_birth")
        self.renames("person:date_of_death", "person_date_of_death")

        self.unprefixes("memorial")

        self.renames("wikipedia:en", "wikipedia_en")
        self.renames("inscription:cs", "inscription_cs")
    @staticmethod
    def accepts(props):
        return "memorial" in props
