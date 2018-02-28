import enum
from datetime import datetime
from . import db

class AreaState(enum.Enum):
    creating = 0
    getting_changes = 1
    applying_changes = 2
    updated = 3

def dt_to_str(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.UnicodeText, nullable=False, unique=True)
    state = db.Column(db.Enum(AreaState), nullable=False, default=AreaState.creating)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def json_dict(self):
        return dict(name=self.name, state=self.state.name, created_at=dt_to_str(self.created_at), updated_at=dt_to_str(self.updated_at))