from . import db, huey
from .models import Area, AreaState
from .area_database_updater import create_database

@huey.task()
def create_database_task(area_name):
    create_database(area_name)
    """area = Area.query.filter_by(name=area_name).first()
    area.state = AreaState.updated
    db.session.commit()"""