use crate::area::{Area, AreaState};
use crate::background_tasks::CreateAreaDatabaseTask;
use crate::names_cache::{CacheMap, OSMObjectNamesCache};
use crate::{DbConn, Error, Result};
use doitlater::{ExecutableExt, Queue};
use osm_db::AreaDatabase;
use redis_api::ChangesStream;
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

#[derive(Deserialize)]
pub struct CreateClientRequest {
    client_id: String,
}

#[derive(Serialize)]
pub struct CreateClientResponse {
    password: String,
}

#[get("/areas")]
pub async fn areas(conn: DbConn) -> Result<Json<Vec<Area>>> {
    let areas = conn.run(|conn| Area::all(conn)).await?;
    Ok(Json(areas))
}

#[post("/areas", format = "json", data = "<request>")]
pub async fn maybe_create_area(
    request: Json<MaybeCreateAreaRequest>,
    conn: DbConn,
) -> Result<status::Custom<Json<Area>>> {
    let area = request.into_inner();
    let area_id = area.osm_id;
    match conn.run(move |c| Area::find_by_osm_id(area_id, c)).await {
        Ok(a) => Ok(status::Custom(Status::Ok, Json(a))),
        Err(_e) => {
            let area = conn
                .run(move |c| Area::create(area.osm_id, &area.name, c))
                .await?;
            let mut queue = Queue::new_from_env()?;
            CreateAreaDatabaseTask::new(area.osm_id)
                .enqueue_into(&mut queue, &format!("create_area_{}", area.osm_id))?;
            Ok(status::Custom(Status::Created, Json(area)))
        }
    }
}

#[get("/areas/<area_osm_id>/download?<client_id>")]
pub async fn download_area(area_osm_id: i64, client_id: String, conn: DbConn) -> Result<File> {
    let area = conn
        .run(move |c| Area::find_by_osm_id(area_osm_id, c))
        .await?;
    if area.state != AreaState::Updated && area.state != AreaState::Frozen {
        Err(Error::DatabaseIntegrityError)
    } else {
        if area.state == AreaState::Updated {
            let mut stream = ChangesStream::new_from_env(area_osm_id)?;
            if stream.has_client(&client_id)? {
                stream.redownload_finished_for(&client_id)?;
                stream.ensure_access_for(&client_id)?;
            } else {
                stream.register_client(&client_id)?;
            }
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

#[post("/create_client", data = "<req>")]
pub async fn create_client(req: Json<CreateClientRequest>) -> Result<Json<CreateClientResponse>> {
    let mut stream = ChangesStream::new_from_env(0)?;
    let client_id = req.into_inner().client_id;
    if stream.has_client(&client_id)? {
        Err(Error::ClientAlreadyExists)
    } else {
        let password = stream.create_client(&client_id)?;
        Ok(Json(CreateClientResponse { password }))
    }
}

#[get("/osm_object_names")]
pub fn osm_object_names() -> Result<Json<CacheMap>> {
    let cache = OSMObjectNamesCache::load()?;
    Ok(Json(cache.into_cache_map()))
}
