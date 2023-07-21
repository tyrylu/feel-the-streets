use crate::area::{Area, AreaState};
use crate::background_tasks::CreateAreaDatabaseTask;
use crate::names_cache::{CacheMap, OSMObjectNamesCache};
use crate::{AppState, Error, Result};
use axum::{
    extract::{Path as ExtractPath, Query, State},
    http::{
        header::{CONTENT_LENGTH, CONTENT_TYPE},
        StatusCode,
    },
    response::{IntoResponse, Json},
    routing::{get, post},
    Router,
};
use axum_extra::body::AsyncReadBody;
use doitlater::{ExecutableExt, Queue};
use osm_db::AreaDatabase;
use redis_api::ChangesStream;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use std::time::SystemTime;
use tokio::fs::{self, File};

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

#[derive(Deserialize)]
struct ClientIdentification {
    client_id: String,
}

pub async fn areas(State(state): State<AppState>) -> Result<Json<Vec<Area>>> {
    let areas = Area::all(&state.db_conn.lock().unwrap())?;
    Ok(Json(areas))
}

async fn maybe_create_area(
    State(state): State<AppState>,
    Json(area): Json<MaybeCreateAreaRequest>,
) -> Result<impl IntoResponse> {
    let area_id = area.osm_id;
    info!("Maybe creating area {}", area_id);
    match Area::find_by_osm_id(area_id, &state.db_conn.lock().unwrap()) {
        Ok(a) => Ok((StatusCode::OK, Json(a))),
        Err(_e) => {
            let area = Area::create(area.osm_id, &area.name, &state.db_conn.lock().unwrap())?;
            info!("Created area {}", area.osm_id);
            let mut queue = Queue::new_from_env()?;
            CreateAreaDatabaseTask::new(area.osm_id)
                .enqueue_into(&mut queue, &format!("create_area_{}", area.osm_id))?;
            ifno!("Enqueued area creation request for area {}", area.osm_id)
            Ok((StatusCode::CREATED, Json(area)))
        }
    }
}

async fn download_area(
    ExtractPath(area_osm_id): ExtractPath<i64>,
    ident: Query<ClientIdentification>,
    State(state): State<AppState>,
) -> Result<impl IntoResponse> {
    let area = Area::find_by_osm_id(area_osm_id, &state.db_conn.lock().unwrap())?;
    if area.state != AreaState::Updated && area.state != AreaState::Frozen {
        Err(Error::DatabaseIntegrityError)
    } else {
        if area.state == AreaState::Updated {
            let mut stream = ChangesStream::new_from_env(area_osm_id)?;
            if stream.has_client(&ident.client_id)? {
                stream.redownload_finished_for(&ident.client_id)?;
                stream.ensure_access_for(&ident.client_id)?;
            } else {
                stream.register_client(&ident.client_id)?;
            }
        }
        let headers = [
            (CONTENT_LENGTH, area.db_size.to_string()),
            (CONTENT_TYPE, "application/octed-stream".to_string()),
        ];
        Ok((
            headers,
            AsyncReadBody::new(File::open(AreaDatabase::path_for(area_osm_id, true)).await?),
        ))
    }
}

pub async fn ping() -> Json<PingResponse> {
    Json(PingResponse {
        response: "pong".to_string(),
    })
}

pub async fn motd() -> Result<Json<HashMap<String, MotdEntry>>> {
    let mut messages = HashMap::new();
    let motd_dir = Path::new("motd");
    if motd_dir.is_dir() {
        for maybe_entry in motd_dir.read_dir()? {
            let entry = maybe_entry?;
            if entry.file_type()?.is_file() {
                let message = fs::read_to_string(entry.path()).await?;
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

pub async fn create_client(req: Json<CreateClientRequest>) -> Result<Json<CreateClientResponse>> {
    let mut stream = ChangesStream::new_from_env(0)?;
    let client_id = &req.client_id;
    if stream.has_client(client_id)? {
        Err(Error::ClientAlreadyExists)
    } else {
        let password = stream.create_client(client_id)?;
        Ok(Json(CreateClientResponse { password }))
    }
}

pub async fn osm_object_names() -> Result<Json<CacheMap>> {
    let cache = OSMObjectNamesCache::load()?;
    Ok(Json(cache.into_cache_map()))
}

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/areas", get(areas).post(maybe_create_area))
        .route("/areas/:area_osm_id/download", get(download_area))
        .route("/ping", get(ping))
        .route("/motd", get(motd))
        .route("/create_client", post(create_client))
        .route("/osm_object_names", get(osm_object_names))
}
