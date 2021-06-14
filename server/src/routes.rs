use crate::area::{Area, AreaState};
use crate::area_messaging;
use crate::background_task::BackgroundTask;
use crate::{DbConn, Error, Result};
use osm_db::AreaDatabase;
use rocket::http::Status;
use rocket::response::status;
use rocket::serde::json::Json;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::{self, File};
use std::path::Path;
use std::time::SystemTime;

#[derive(Deserialize)]
pub struct MaybeCreateAreaRequest {
    osm_id: i64,
    name: String,
}

#[derive(Serialize)]
pub struct PingResponse {
    response: String,
}

#[derive(Serialize)]
pub struct MotdEntry {
    timestamp: u64,
    message: String,
}

#[get("/areas")]
pub async fn areas(conn: DbConn) -> Result<Json<Vec<Area>>> {
    let areas = conn.run(|conn| Area::all(&conn)).await?;
    Ok(Json(areas))
}

#[post("/areas", format = "json", data = "<request>")]
pub async fn maybe_create_area(
    request: Json<MaybeCreateAreaRequest>,
    conn: DbConn,
) -> Result<status::Custom<Json<Area>>> {
    let area = request.into_inner();
    let area_id = area.osm_id;
    match conn.run(move |c| {Area::find_by_osm_id(area_id, &c)}).await {
        Ok(a) => Ok(status::Custom(Status::Ok, Json(a))),
        Err(_e) => {
                        let area = conn.run(move |c| {Area::create(area.osm_id, &area.name, &c)}).await?;
            area_messaging::init_exchange(area.osm_id)?;
            BackgroundTask::CreateAreaDatabase(area.osm_id).deliver()?;
            Ok(status::Custom(Status::Created, Json(area)))
        }
    }
}

#[get("/areas/<area_osm_id>/download?<client_id>")]
pub async fn download_area(area_osm_id: i64, client_id: String, conn: DbConn) -> Result<File> {
    let area = conn.run(move |c| {Area::find_by_osm_id(area_osm_id, &c)}).await?;
    if area.state != AreaState::Updated && area.state != AreaState::Frozen {
        Err(Error::DatabaseIntegrityError)
    } else {
        if area.state == AreaState::Updated {
            area_messaging::init_queue(&client_id, area_osm_id)?;
        }
        Ok(File::open(AreaDatabase::path_for(area_osm_id, true))?)
    }
}

#[get("/ping")]
pub fn ping() -> Json<PingResponse> {
    Json(PingResponse {
        response: "pong".to_string(),
    })
}

#[get("/motd")]
pub fn motd() -> Result<Json<HashMap<String, MotdEntry>>> {
    let mut messages = HashMap::new();
    let motd_dir = Path::new("motd");
    if motd_dir.is_dir() {
        for maybe_entry in motd_dir.read_dir()? {
            let entry = maybe_entry?;
            if entry.file_type()?.is_file() {
                let message = fs::read_to_string(entry.path())?;
                let timestamp = entry
                    .metadata()?
                    .modified()?
                    .duration_since(SystemTime::UNIX_EPOCH)?
                    .as_secs();
                messages.insert(
                    entry.file_name().to_string_lossy().to_string(),
                    MotdEntry { timestamp, message },
                );
            }
        }
    }
    Ok(Json(messages))
}
