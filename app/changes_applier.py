import os
import datetime
import logging
from PySide6.QtCore import QThread, Signal
from osm_db import AreaDatabase
from osm_db import ChangeType as CT
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
        if self._generate_changelog:
            changelog_path = os.path.join(os.path.dirname(AreaDatabase.path_for(12345, server_side=False)), "..", "changelogs", "{0}_{1}.txt".format(self._area, datetime.datetime.now().isoformat().replace(":", "_")))
            os.makedirs(os.path.dirname(changelog_path), exist_ok=True)
            changelog = open(changelog_path, "w", encoding="UTF-8")
        else:
            changelog_path = None
        changes_applyed = False
        for nth, change in enumerate(self._retriever.new_changes_in(self._area)):
            self.will_process_change.emit(nth + 1)
            entity = None
            # We must retrieve the entity before deleting it so we can produce the display representation of it.
            if self._generate_changelog and change.type == CT.Remove:
                entity = db.get_entity(change.osm_id)
            db.apply_change(change)
            changes_applyed = True
            if self._generate_changelog:
                if not entity:
                    entity = db.get_entity(change.osm_id)
                    if not entity:
                        log.error("Local database is missing entity with osm id %s, not generating changelog description for that one.", change.osm_id)
                        continue
                changelog.write(get_change_description(change, entity))
        db.apply_deferred_relationship_additions()
        db.commit()
        if self._generate_changelog:
            changelog.close()
        self._retriever.acknowledge_changes_for(self._area)
        self._retriever.close()
        if changes_applyed:
            self.changes_applied.emit(changelog_path)
        