from .annotated import AnnotatedGenerator
from shared.models import Notice

class NoticeGenerator(AnnotatedGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Notice)
        self.unprefixes("seamark:notice")

    @staticmethod
    def accepts(props):
        return AnnotatedGenerator.accepts(props) and "seamark:type" in props and props["seamark:type"] == "notice"