from .building import BuildingGenerator
from shared.models import Shop

class ShopGenerator(BuildingGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Shop)
        self.renames("shop", "type")
        self.renames("vehicle:parts", "vehicle_parts")
        self.renames("vehicle:repair", "vehicle_repair")
        self.renames("payment:coins", "coins_payment")
        self.renames("payment:notes", "notes_payment")
        self.renames("payment:maestro", "maestro_payment")
        self.renames("payment:mastercard", "mastercard_payment")
        self.renames("payment:visa", "visa_payment")
        self.renames("payment:bitcoin", "bitcoin_payment")
        self.renames("secondhand", "second_hand")
        self.unprefixes("drink")
        self.removes_subtree("service")
        self.removes("siing")
        
    def _prepare_properties(self, entity_spec, props, record):        
        props["shop"] = props["shop"].replace(";", "_")
        if "sport" in props:
            props["sport"] = props["sport"].replace(";", "_")
        return super()._prepare_properties(entity_spec, props, record)

    @staticmethod
    def accepts(props):
        return BuildingGenerator.accepts(props) and "shop" in props