from PySide6.QtCore import Signal, QThread
import os
import logging
import xml.etree.ElementTree as et
import requests
import atomicwrites
from ..services import config
from ..local_utils import cache_response, get_cached_response, get_local_area_ids
from .motd import Motd
from osm_db import AreaDatabase

API_ENDPOINT = os.environ.get("API_ENDPOINT", "https://fts.trycht.cz/api")
HAS_API_CONNECTIVITY = None

log = logging.getLogger(__name__)

session = requests.Session()

class RateLimitedError(Exception): pass

def url_for(path):
    return "{0}/{1}".format(API_ENDPOINT, path)

def get_areas_with_name(name):
    query = f'[out:json];area["name"="{name}"];out meta;'
    resp = requests.get("https://overpass-api.de/api/interpreter", params={"data": query})
    if resp.status_code != 200:
        raise RateLimitedError()
    results = {}
    for area in resp.json()["elements"]:
        if "admin_level" not in area["tags"]:
            continue
        results[area["id"]] = area["tags"]
    return results

def get_areas():
    if not has_api_connectivity():
        data = get_cached_response("areas.json")
        if not data:
            log.warning("No cached areas data found.")
            return None
        local_ids = get_local_area_ids()
        local_data = []
        for area in data:
            if area["osm_id"] in local_ids:
                area["state"] = "Local"
                local_data.append(area)
        return local_data
    else:
        resp = session.get(url_for("areas"))
        if resp.status_code == 200:
            data = resp.json()
            cache_response("areas.json", data)
            return data
        else:
            log.warning("Non 200 response during areas request, status code %s.", resp.status_code)
            return None

def request_area_creation(area_id, area_name):
    resp = session.post(url_for("areas"), json={"name": area_name, "osm_id": area_id})
    if resp.status_code in {200, 201}:
        return resp.json()
    else:
        log.warning("Unexpected status code during an area creation request: %s, response %s.", resp.status_code, resp.content)
        return None

class AreaDatabaseDownloader(QThread):
    download_progressed = Signal(int, int)
    download_finished = Signal(bool)

    def __init__(self, area):
        super().__init__()
        self._area = area

    def run(self):
        resp = session.get(url_for("areas/{0}/download".format(self._area)), stream=True, params={"client_id": config().general.client_id})
        if resp.status_code == 200:
            total = int(resp.headers.get("content-length", 0))
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
            log.warning("Non 200 status code during area download: %s.", resp.status_code)
            self.download_finished.emit(False)

def has_api_connectivity():
    global HAS_API_CONNECTIVITY
    if HAS_API_CONNECTIVITY is not None:
        return HAS_API_CONNECTIVITY
    result = None
    try:
        resp = session.get(url_for("ping"))
        if resp.status_code != 200:
            result = False
        else:
            result = True
    except requests.ConnectionError:
        result = False
    HAS_API_CONNECTIVITY = result
    return result

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

def get_motd():
    if not has_api_connectivity():
        return None
    resp = session.get(url_for("motd"))
    if resp.status_code != 200:
        log.warning("Motd request returned with status %s.", resp.status_code)
        return None
    data = resp.json()
    if not data: # No motd has been published yet
        return None
    return Motd(data)

def create_client(client_id):
    resp = session.post(url_for("create_client"), json={"client_id":client_id})
    print(resp.content, resp.status_code)
    if resp.status_code == 200:
        return resp.json()["password"]

def get_osm_object_names(from_cache=False):
    if has_api_connectivity() and not from_cache:
        data = session.get(url_for("osm_object_names")).json()
        cache_response("osm_object_names.json", data)
        return data
    else:
        return get_cached_response("osm_object_names.json")