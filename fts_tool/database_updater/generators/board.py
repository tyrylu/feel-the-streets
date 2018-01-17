from .tourism import TourismGenerator
from shared.models import Board

class BoardGenerator(TourismGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Board)

        self.renames("language:cs", "language_cs")
    def _prepare_properties(self, entity_spec, props, record):
        if "board_type" in props: props["board_type"] = props["board_type"].replace(";", "_")
        props = super()._prepare_properties(entity_spec, props, record)
        return props

    @staticmethod
    def accepts(props):
        return TourismGenerator.accepts(props) and "information" in props and props["information"] == "board"
