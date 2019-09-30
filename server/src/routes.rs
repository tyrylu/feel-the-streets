use crate::area::{Area, AreaState};
use crate::area_messaging;
use crate::background_task::BackgroundTask;
use crate::DbConn;
use crate::Result;
use failure::bail;
use osm_db::AreaDatabase;
use rocket::http::Status;
use rocket::response::status;
use rocket_contrib::json::Json;
use serde::{Deserialize, Serialize};
use std::fs::File;

#[derive(Deserialize)]
pub struct MaybeCreateAreaRequest {
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
    let area_name = request.into_inner().name;
    match Area::find_by_name(&area_name, &*conn) {
        Ok(a) => Ok(status::Custom(Status::Ok, Json(a))),
        Err(_e) => {
            let area = Area::create(&area_name, &*conn)?;
            area_messaging::init_exchange(&area_name)?;
            BackgroundTask::CreateAreaDatabase(area_name).deliver()?;
            Ok(status::Custom(Status::Created, Json(area)))
        }
    }
}

#[get("/areas/<area_name>/download?<client_id>")]
pub fn download_area(area_name: String, client_id: String, conn: DbConn) -> Result<File> {
    let area = Area::find_by_name(&area_name, &*conn)?;
    if area.state != AreaState::Updated {
        bail!("Can not guarantee area data integrity.")
    } else {
        area_messaging::init_queue(&client_id, &area_name)?;
        Ok(File::open(AreaDatabase::path_for(&area_name, true))?)
    }
}

#[get("/ping")]
pub fn ping() -> Json<PingResponse> {
    Json(PingResponse {
        response: "pong".to_string(),
    })
}
