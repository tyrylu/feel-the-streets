from sqlalchemy import Column, ForeignKey, Integer, UnicodeText
from .entity import Entity

class Named(Entity):
    __tablename__ = "named"
    __mapper_args__ = {'polymorphic_identity': 'named'}
    id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    name = Column(UnicodeText)
    
    def __str__(self):
        inherited = super().__str__()
        if self.name:
            inherited += " " + self.name
        return  inherited