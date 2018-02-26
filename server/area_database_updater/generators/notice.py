from .annotated import AnnotatedGenerator
from shared.entities import Notice

class NoticeGenerator(AnnotatedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Notice)
        self.renames("seamark:type", "type")
        self.unprefixes("seamark:notice")
        self.unprefixes("notice")

    @staticmethod
    def accepts(props):
        return AnnotatedGenerator.accepts(props) and "seamark:type" in props and props["seamark:type"] == "notice"