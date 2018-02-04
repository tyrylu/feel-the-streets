from .address_aware import AddressAwareGenerator
from shared.entities import Pub

class PubGenerator(AddressAwareGenerator):
    def __init__(self):
        super().__init__()
        self.generates(Pub)
        self.unprefixes("contact")
        self.unprefixes("building")

        self.renames("internet_access:fee", "internet_access_fee")
        self.renames("payment:other", "other_payment")
        self.renames("payment:cash", "cash_payment")
        self.renames("payment:debit_cards", "debitcards_payment")
        self.renames("payment:litecoin", "litecoin_payment")
        self.renames("payment:ethereum", "ethereum_payment")
        self.renames("payment:meal_vouchers", "meal_vouchers_payment")
        self.renames("payment:jcb", "jcb_payment")
        self.renames("payment:visa", "visa_payment")
        self.renames("payment:cryptocurrencies", "cryptocurrencies_payment")
    @staticmethod
    def accepts(props):
        return "amenity" in props and props["amenity"] == "pub"