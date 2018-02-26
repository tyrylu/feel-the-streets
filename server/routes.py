from flask import jsonify, request, Response, send_file, abort
from . import app, db
from .models import Area, AreaState
from .tasks import create_database
from shared import Database

@app.route("/api/areas", methods=["GET"])
def areas():
    return jsonify(Area.query.all())

@app.route("/api/areas", methods=["POST"])
def maybe_create_area():
    json_body = request.get_json()
    if json_body and isinstance(json_body, dict):
        name = json_body.get("name", None)
    if not json_body or not name:
        abort(400)
    area = Area.query.get(name=name)
    if area:
        return jsonify(area)
    else:
        area = Area(name=name)
        db.session.add(area)
        db.session.commit()
        resp = jsonify(area)
        resp.status_code = 201
        create_database(name)
        return resp

@app.route("/api/areas/<area_name>")
def area_detail(area_name):
    area = Area.query.filter_by(name=area_name).first_or_404()
    return jsonify(area)

@app.route("/api/areas/<area_name>/download")
def download_area_data(area_name):
    area = Area.query.filter_by(name=area_name).first_or_404()
    if area.state in {AreaState.creating, AreaState.applying_changes}:
        # We can not guarantee data integrity in those cases. The database is incomplete, or the client could get partial changes from the queue or none at all.
        abort(400)
    else:
        return send_file(Database.get_database_file(area_name))
