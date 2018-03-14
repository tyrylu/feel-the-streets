import os

class OSMObjectBlacklist:

    def __init__(self):
        self._blacklisted = set()
        self._blacklist_path = os.path.join(os.path.dirname(__file__), "..", "osm_object_blacklist")
        if os.path.exists(self._blacklist_path):
            self._load()


    def _load(self):
        with open(self._blacklist_path, "r") as fp:
            for line in fp:
                line = line.strip()
                if line:
                    self._blacklisted.add(line)

    def save(self):
        if self._blacklisted:
            with open(self._blacklist_path, "w") as fp:
                for entry in self._blacklisted:
                    fp.write("{0}\n".format(entry))
    def __contains__(self, entry):
        return entry in self._blacklisted

    def add(self, entry):
        self._blacklisted.add(entry)