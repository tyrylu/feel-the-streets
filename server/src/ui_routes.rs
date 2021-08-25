use std::collections::HashMap;

use crate::area::Area;
use crate::{DbConn, Result};
use redis_api::ChangesStream;
use rocket_dyn_templates::Template;

#[get("/areas")]
pub async fn areas(conn: DbConn) -> Result<Template> {
    
    #[derive(serde::Serialize)]
    struct StreamInfo {
        len: usize,
        memory_usage: u64,
        number_of_clients: usize
    }

    #[derive(serde::Serialize)]
    struct TCtxt {
        areas: Vec<Area>,
        stream_infos: HashMap<i32, StreamInfo>
    }
    let areas = conn.run(|conn| Area::all(conn)).await?;
    let mut ctx = TCtxt { areas, stream_infos: HashMap::new()};
    let mut stream = ChangesStream::new_from_env(0)?;
    for area in &ctx.areas {
        stream.connect_to_stream(area.osm_id);
        ctx.stream_infos.insert(area.id, StreamInfo { len: stream.len()?, memory_usage: stream.memory_usage()?, number_of_clients: stream.registered_clients()?.len()});
    }
    Ok(Template::render("areas", ctx))
}

#[get("/areas/<area_id>")]
pub async fn area_detail(area_id: i32, conn: DbConn) -> Result<Template> {
    #[derive(serde::Serialize)]
    struct Tctxt {
        area: Area,
        change_counts: HashMap<String, u64>,
        redownload_requests: Vec<String>
    }
    let area = conn
    .run(move |c| Area::find_by_id(area_id, c))
    .await?;
    let mut stream = ChangesStream::new_from_env(area.osm_id)?;
    let redownload_requests = stream.all_redownload_requests()?;
    let change_counts = stream.all_change_counts()?;
    Ok(Template::render("area_detail", Tctxt {area, change_counts, redownload_requests}))


}