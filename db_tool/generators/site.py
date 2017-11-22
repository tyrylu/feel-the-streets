from .named import NamedGenerator
from shared.models import Site

class SiteGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Site)

    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "site"