from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from .bookmark import Bookmark
from .last_location import LastLocation