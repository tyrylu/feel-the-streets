from .boundary import BoundaryGenerator
from shared.models import Border

class BorderGenerator(BoundaryGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Border)
        self.renames("left:country", "left_country")
        self.renames("right:country", "right_country")
        

    @staticmethod
    def accepts(props):
        return BoundaryGenerator.accepts(props) and "border_type" in props