use crate::area::Area;
use crate::{AppState, Result};
use askama::Template;
use axum::{
    extract::{Path, State},
    response::Html,
    routing::get,
    Router,
};
use osm_db::AreaDatabase;
use redis_api::ChangesStream;
use std::collections::HashMap;

pub async fn areas(State(state): State<AppState>) -> Result<Html<String>> {
    struct StreamInfo {
        len: usize,
        memory_usage: u64,
        number_of_clients: usize,
    }

    #[derive(Template)]
    #[template(path = "areas.html")]
    struct TCtxt {
        areas: Vec<Area>,
        stream_infos: HashMap<i32, StreamInfo>,
    }
    let areas = Area::all(&state.db_conn.lock().unwrap())?;
    let mut ctx = TCtxt {
        areas,
        stream_infos: HashMap::new(),
    };
    let mut stream = ChangesStream::new_from_env(0)?;
    for area in &ctx.areas {
        stream.connect_to_stream(area.osm_id);
        ctx.stream_infos.insert(
            area.id,
            StreamInfo {
                len: stream.len()?,
                memory_usage: stream.memory_usage()?,
                number_of_clients: stream.registered_clients()?.len(),
            },
        );
    }
    Ok(Html(ctx.render()?))
}

pub async fn area_detail(
    Path(area_id): Path<i32>,
    State(state): State<AppState>,
) -> Result<Html<String>> {
    #[derive(Template)]
    #[template(path = "area_detail.html")]
    struct Tctxt {
        area: Area,
        change_counts: HashMap<String, u64>,
        redownload_requests: Vec<String>,
        entity_count: usize,
        entity_relationship_count: usize,
        entity_counts: HashMap<String, usize>,
        relationship_counts: HashMap<String, usize>,
    }
    let area = Area::find_by_id(area_id, &state.db_conn.lock().unwrap())?;
    let mut stream = ChangesStream::new_from_env(area.osm_id)?;
    let redownload_requests = stream.all_redownload_requests()?;
    let change_counts = stream.all_change_counts()?;
    let area_db = AreaDatabase::open_existing(area.osm_id, true)?;
    let entity_count = area_db.num_entities()?;
    let entity_relationship_count = area_db.num_entity_relationships()?;
    let entity_counts = area_db.get_entity_counts_by_discriminator()?;
    let relationship_counts = area_db.get_entity_relationship_counts_by_kind()?;
    Ok(Html(Tctxt {
            area,
            change_counts,
            redownload_requests,
            entity_count,
            entity_relationship_count,
            entity_counts,
            relationship_counts,
        }.render()?,
    ))
}

pub fn routes() -> Router<AppState> {
    Router::new()
        .route("/areas", get(areas))
        .route("/areas/{area_id}", get(area_detail))
}
