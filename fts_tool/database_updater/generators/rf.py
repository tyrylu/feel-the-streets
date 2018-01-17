from .named import NamedGenerator
from shared.models import RF

class RFGenerator(NamedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(RF)

        self.renames("rf:category", "category")
        self.renames("rf:modulation", "modulation")
        self.renames("ant:power", "power")
        self.renames("rf:content", "content")
        self.renames("fm:stereo", "stereo")
        self.renames("rds:pi", "pi")
        self.renames("dvbt:parameters", "dvbt_parameters")
        self.renames("rf:owner", "owner")
        self.renames("rf:callsign", "callsign")
    @staticmethod
    def accepts(props):
        return NamedGenerator.accepts(props) and "type" in props and props["type"] == "rf"
