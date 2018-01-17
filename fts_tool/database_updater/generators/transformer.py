from .power import PowerGenerator
from shared.models import Transformer

class TransformerGenerator(PowerGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Transformer)
        self.renames("transformer", "transformer_type")

    @staticmethod
    def accepts(props):
        return PowerGenerator.accepts(props) and "transformer" in props
