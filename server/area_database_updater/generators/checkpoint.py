from .generator import Generator
from shared.entities import Checkpoint

class CheckpointGenerator(Generator):
    def __init__(self):
        super().__init__()
        self.generates(Checkpoint)
        self.renames("checkpoint", "type")
        self.renames("checkpoint:name", "checkpoint_name")
        self.renames("checkpoint:type", "checkpoint_type")

    @staticmethod
    def accepts(props):
        return "checkpoint" in props