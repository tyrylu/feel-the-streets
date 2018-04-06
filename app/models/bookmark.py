from sqlalchemy import Column, Float, Integer, UnicodeText
from . import Base

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True)
    area = Column(UnicodeText, nullable=False)
    name = Column(UnicodeText, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)