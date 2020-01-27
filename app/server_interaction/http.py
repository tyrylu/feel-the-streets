import os
import logging
import requests
from ..services import config
from osm_db import AreaDatabase

if os.environ.get("API_DEBUG", "0") == "1":
    API_ENDPOINT = "http://localhost:5000/api"
else:
    API_ENDPOINT = "https://fts.trycht.cz/api"
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

def download_area_database(area_id, progress_callback=None):
    resp = session.get(url_for("areas/{0}/download".format(area_id)), stream=True, params={"client_id": config().client_id})
    if resp.status_code == 200:
        total = int(resp.headers.get("content-length", 0))
        chunk_size = 32*1024
        db_path = AreaDatabase.path_for(area_id, server_side=False)
        dbs_dir = os.path.dirname(db_path)
        os.makedirs(dbs_path, exist_ok=True)
        fp = open(db_path, "wb")
        so_far = 0
        for chunk in resp.iter_content(chunk_size):
            so_far += len(chunk)
            fp.write(chunk)
            if progress_callback:
                progress_callback(total, so_far)
        fp.close()
        return True
    else:
        log.warn("Non 200 status code during area download: %s.", resp.status_code)
        return False

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