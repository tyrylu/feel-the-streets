use chrono::Utc;
use log::info;
use osm_api::object_manager::OSMObjectManager;
use osm_api::overpass_api::Servers;
use server::names_cache::OSMObjectNamesCache;
use server::{area::Area, background_tasks::area_db_creation, db, Result};
use std::fs;
use std::path::Path;
use std::sync::{Arc, Mutex};

async fn async_main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    let now = Utc::now();
    info!("Recreating all areas as of {}.", now);
    let server_conn = Arc::new(Mutex::new(db::connect_to_server_db()?));
    let servers = Arc::new(Servers::default());
    let cache = Arc::new(osm_api::object_manager::open_cache(Some(&now))?);
    let names_cache = Arc::new(Mutex::new(OSMObjectNamesCache::load()?));
    let mut tasks = vec![];
    for area in Area::all(&server_conn.lock().unwrap())? {
        let area_file = format!("{}.db", area.osm_id);
        if Path::new(&area_file).exists() {
            fs::remove_file(&area_file)?;
        }
        info!("Recreating area {}...", area.name);
        let manager =
            OSMObjectManager::new_multithread(Some(&now), servers.clone(), cache.clone())?;
        let server_conn_clone = server_conn.clone();
        let names_cache_clone = names_cache.clone();
        tasks.push(tokio::task::spawn_blocking(move || {
            area_db_creation::create_area_database_worker(
                area.osm_id,
                manager,
                server_conn_clone,
                names_cache_clone,
            )
        }));
    }
    for task in tasks {
        if let Err(e) = task.await {
            println!("Failed to recreate area, error: {e}");
        }
    }
    names_cache.lock().unwrap().save()?;
    Ok(())
}

fn main() -> Result<()> {
    tokio::runtime::Builder::new_multi_thread()
        .enable_all()
        .thread_stack_size(4 * 1024 * 1024)
        .build()
        .unwrap()
        .block_on(async_main())
}
