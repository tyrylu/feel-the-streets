from .historic import HistoricGenerator
from shared.models import Memorial

class MemorialGenerator(HistoricGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Memorial)
        self.renames("memorial:type", "memorial_type")
        self.renames("memorial", "memorial_kind")

    @staticmethod
    def accepts(props):
        return HistoricGenerator.accepts(props) and props["historic"] == "memorial"