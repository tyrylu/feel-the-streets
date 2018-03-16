import os
import logging
import requests
from ..services import config
from shared import Database

if os.environ.get("API_DEBUG", "0") == "1":
    API_ENDPOINT = "http://localhost:5000/api"
else:
    API_ENDPOINT = "https://fts.trycht.cz/api"
log = logging.getLogger(__name__)

def url_for(path):
    return "{0}/{1}".format(API_ENDPOINT, path)

def get_areas():
    resp = requests.get(url_for("areas"))
    if resp.status_code == 200:
        return resp.json()
    else:
        log.warn("Non 200 response during areas request, status code %s.", resp.status_code)
        return None

def request_area_creation(area_name):
    resp = requests.post(url_for("areas"), json={"name": area_name})
    if resp.status_code in {200, 201}:
        return resp.json()
    else:
        log.warn("Unexpected status code during an area creation request: %s, response %s.", resp.status_code, resp.content)
        return None

def download_area_database(area_name, progress_callback=None):
    resp = requests.get(url_for("areas/{0}/download".format(area_name)), stream=True, params={"client_id": config().client_id})
    if resp.status_code == 200:
        total = int(resp.headers.get("content-length", 0))
        chunk_size = 32*1024
        fp = open(Database.get_database_file(area_name, server_side=False), "wb")
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
        resp = requests.get(url_for("ping"))
        if not resp.status_code == 200:
            return False
        else:
            return True
    except requests.ConnectionError:
        return False