use crate::area::{Area, AreaState};
use crate::area_messaging;
use crate::background_task::BackgroundTask;
use crate::{DbConn, Error, Result};
use osm_db::AreaDatabase;
use rocket::http::Status;
use rocket::response::status;
use rocket_contrib::json::Json;
use serde::{Deserialize, Serialize};
use std::fs::File;

#[derive(Deserialize)]
pub struct MaybeCreateAreaRequest {
    osm_id: i64,
    name: String,
}

#[derive(Serialize)]
pub struct PingResponse {
    response: String,
}

#[get("/areas")]
pub fn areas(conn: DbConn) -> Result<Json<Vec<Area>>> {
    Ok(Json(Area::all(&*conn)?))
}

#[post("/areas", format = "json", data = "<request>")]
pub fn maybe_create_area(
    request: Json<MaybeCreateAreaRequest>,
    conn: DbConn,
) -> Result<status::Custom<Json<Area>>> {
    let area = request.into_inner();
    match Area::find_by_osm_id(area.osm_id, &*conn) {
        Ok(a) => Ok(status::Custom(Status::Ok, Json(a))),
        Err(_e) => {
            let area = Area::create(area.osm_id, &area.name, &*conn)?;
            area_messaging::init_exchange(area.osm_id)?;
            BackgroundTask::CreateAreaDatabase(area.osm_id).deliver()?;
            Ok(status::Custom(Status::Created, Json(area)))
        }
    }
}

#[get("/areas/<area_osm_id>/download?<client_id>")]
pub fn download_area(area_osm_id: i64, client_id: String, conn: DbConn) -> Result<File> {
    let area = Area::find_by_osm_id(area_osm_id, &*conn)?;
    if area.state != AreaState::Updated {
        Err(Error::DatabaseIntegrityError)
    } else {
        area_messaging::init_queue(&client_id, area_osm_id)?;
        Ok(File::open(AreaDatabase::path_for(area_osm_id, true))?)
    }
}

#[get("/ping")]
pub fn ping() -> Json<PingResponse> {
    Json(PingResponse {
        response: "pong".to_string(),
    })
}
