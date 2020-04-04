import os
import json
import datetime
import logging
from PySide2.QtCore import QThread, Signal
from osm_db import AreaDatabase, CHANGE_REMOVE
from .semantic_changelog_generator import get_change_description


log = logging.getLogger(__name__)

class ChangesApplier(QThread):
    will_process_change = Signal(int)
    changes_applied = Signal(str)
    
    def __init__(self, area, retriever, generate_changelog):
        super().__init__()
        self._area = area
        self._retriever = retriever
        self._generate_changelog = generate_changelog

    def run(self):
        db = AreaDatabase.open_existing(self._area, server_side=False)
        db.begin()
        changelog_path = os.path.join(os.path.dirname(AreaDatabase.path_for(12345, server_side=False)), "..", "changelogs", "{0}_{1}.txt".format(self._area, datetime.datetime.now().isoformat().replace(":", "_")))
        os.makedirs(os.path.dirname(changelog_path), exist_ok=True)
        changelog = open(changelog_path, "w", encoding="UTF-8")
        for nth, change in enumerate(self._retriever.new_changes_in(self._area)):
            self.will_process_change.emit(nth + 1)
            entity = None
            if self._generate_changelog and change.type is CHANGE_REMOVE:
                entity= db.get_entity(change.osm_id)
            db.apply_change(change)
            if self._generate_changelog:
                if not entity:
                    if change.osm_id:
                        entity = db.get_entity(change.osm_id)
                        if not entity:
                            log.error("Local database is missing entity with osm id %s, not generating changelog description for that one.", change.osm_id)
                            continue
                    else:
                        # This is somewhat ugly, but we really don't have the entity id in any other place and we need its discriminator.
                        data = [c.new_value for c in change.property_changes if c.key == "data"][0]
                        entity = db.get_entity(json.loads(data)["osm_id"])
                        if not entity:
                            log.error("No entity for osm id %s.", data["osm_id"])
                            continue
                changelog.write(get_change_description(change, entity))
        db.commit()
        changelog.close()
        self._retriever.acknowledge_changes_for(self._area)
        self.changes_applied.emit(changelog_path)
        