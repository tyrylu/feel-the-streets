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
    let areas = conn.run(|conn| Area::all(&conn)).await?;
    let mut ctx = TCtxt { areas: areas, stream_infos: HashMap::new()};
    let mut stream = ChangesStream::new_from_env(0)?;
    for area in &ctx.areas {
        stream.connect_to_stream(area.osm_id);
        ctx.stream_infos.insert(area.id, StreamInfo { len: stream.len()?, memory_usage: stream.memory_usage()?, number_of_clients: stream.registered_clients()?.len()});
    }
    Ok(Template::render("areas", ctx))
}
