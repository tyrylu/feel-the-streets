from PySide2.QtCore import QObject, Signal, QThread
import os
import logging
import xml.etree.ElementTree as et
import requests
import atomicwrites
from ..services import config
from osm_db import AreaDatabase

API_ENDPOINT = os.environ.get("API_ENDPOINT", "https://fts.trycht.cz/api")

log = logging.getLogger(__name__)

session = requests.Session()

def url_for(path):
    return "{0}/{1}".format(API_ENDPOINT, path)

def get_areas_with_name(name):
    query = f'[out:json];area["name"="{name}"];out meta;'
    resp = requests.get("https://overpass-api.de/api/interpreter", params={"data": query})
    results = {}
    for area in resp.json()["elements"]:
        if "admin_level" not in area["tags"]:
            continue
        results[area["id"]] = area["tags"]
    return results

def get_areas():
    resp = session.get(url_for("areas"))
    if resp.status_code == 200:
        return resp.json()
    else:
        log.warn("Non 200 response during areas request, status code %s.", resp.status_code)
        return None

def request_area_creation(area_id, area_name):
    resp = session.post(url_for("areas"), json={"name": area_name, "osm_id": area_id})
    if resp.status_code in {200, 201}:
        return resp.json()
    else:
        log.warn("Unexpected status code during an area creation request: %s, response %s.", resp.status_code, resp.content)
        return None


class AreaDatabaseDownloader(QThread):
    download_progressed = Signal(int, int)
    download_finished = Signal(bool)

    def __init__(self, area, parent):
        super().__init__()
        self._area = area

    def __del__(self):
        print("Goodbye?")


    def run(self):
        print("Start.")
        resp = session.get(url_for("areas/{0}/download".format(self._area)), stream=True, params={"client_id": config().general.client_id})
        print(f"We have a response with status {resp.status_code}")
        if resp.status_code == 200:
            total = int(resp.headers.get("content-length", 0))
            print(f"Total size: {total}")
            chunk_size = 32*1024
            db_path = AreaDatabase.path_for(self._area, server_side=False)
            dbs_dir = os.path.dirname(db_path)
            os.makedirs(dbs_dir, exist_ok=True)
            with atomicwrites.atomic_write(db_path, overwrite=True, mode="wb") as fp:
                so_far = 0
                for chunk in resp.iter_content(chunk_size):
                    so_far += len(chunk)
                    fp.write(chunk)
                    self.download_progressed.emit(total, so_far)
            self.download_finished.emit(True)
        else:
            log.warn("Non 200 status code during area download: %s.", resp.status_code)
            self.download_finished.emit(False)

def has_api_connectivity():
    try:
        resp = session.get(url_for("ping"))
        resp.content
        if not resp.status_code == 200:
            return False
        else:
            return True
    except requests.ConnectionError:
        return False

def get_area_parents(area_id):
    if area_id > 3600000000:
        type = "relation"
        id = area_id - 3600000000
    else:
        type = "way"
        id = area_id - 2400000000
    resp = requests.get(f"https://openstreetmap.org/api/0.6/{type}/{id}/relations")
    doc = et.fromstring(resp.text)
    res = {}
    for rel in doc:
        tags = {}
        for tag in rel.findall("tag"):
            tags[tag.attrib["k"]] = tag.attrib["v"]
        res[rel.attrib["id"]] = tags
    return res