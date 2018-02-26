from .named import NamedGenerator
from shared.entities import Site

class SiteGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Site)
        self.renames("site", "type")

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "site"