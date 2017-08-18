from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from . import Named

class Graveyard(Named):
    __tablename__ = "graveyards"
    __mapper_args__ = {'polymorphic_identity': 'graveyard'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    religion = Column(UnicodeText)
    wikidata = Column(UnicodeText)
    wikipedia = Column(UnicodeText)