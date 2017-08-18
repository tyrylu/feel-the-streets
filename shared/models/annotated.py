from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from . import Named

class Annotated(Named):
    __tablename__ = "annotated"
    __mapper_args__ = {'polymorphic_identity': 'annotated'}
    id = Column(Integer, ForeignKey("named.id"), primary_key=True)
    note = Column(UnicodeText)
    fixme = Column(UnicodeText)