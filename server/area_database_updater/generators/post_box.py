from .generator import Generator
from shared.entities import PostBox

class PostBoxGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(PostBox)

    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "post_box"