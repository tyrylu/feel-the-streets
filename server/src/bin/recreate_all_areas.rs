extern crate server;
use diesel::{Connection, SqliteConnection};
use osm_api::object_manager::OSMObjectManager;
use osm_api::overpass_api::Servers;
use server::names_cache::OSMObjectNamesCache;
use server::{area::Area, background_tasks::area_db_creation, Result};
use std::fs;
use std::path::Path;
use std::sync::{Arc, Mutex};

fn main() -> Result<()> {
    let _dotenv_path = dotenvy::dotenv()?;
    server::init_logging();
    let pool = rusty_pool::ThreadPool::default();
    let server_conn = Arc::new(Mutex::new(SqliteConnection::establish("server.db")?));
    let servers = Arc::new(Servers::default());
    let cache = Arc::new(osm_api::object_manager::open_cache()?);
    let names_cache = Arc::new(Mutex::new(OSMObjectNamesCache::load()?));
    let mut tasks = vec![];
    for area in Area::all(&server_conn.lock().unwrap())? {
        let area_file = format!("{}.db", area.osm_id);
        if Path::new(&area_file).exists() {
            fs::remove_file(&area_file)?;
        }
        println!("Recreating area {}...", area.name);
        let manager = OSMObjectManager::new_multithread(servers.clone(), cache.clone())?;
        let server_conn_clone = server_conn.clone();
        let names_cache_clone = names_cache.clone();
        tasks.push(pool.evaluate(move || {
            area_db_creation::create_area_database_worker(
                area.osm_id,
                manager,
                server_conn_clone,
                names_cache_clone,
            )
        }));
    }
    for task in tasks {
        if let Err(e) = task.await_complete() {
            println!("Failed to recreate area, error: {}", e);
        }
    }
    names_cache.lock().unwrap().save()?;
    Ok(())
}
