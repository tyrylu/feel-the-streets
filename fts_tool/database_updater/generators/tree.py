from .natural import NaturalGenerator
from shared.entities import Tree

class TreeGenerator(NaturalGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Tree)
        self.renames("taxon:cs", "taxon_cs")
        self.renames("genus:cz", "genus_cs")
        self.renames("species:cs", "species_cs")


        self.renames("genus:en", "genus_en")
    @staticmethod
    def accepts(props):
        return NaturalGenerator.accepts(props) and props["natural"] in {"tree", "tree_row"}