use anyhow::Result;
use redis_api::ChangesStream;
use server::db;
use server::area::{Area, AreaState};

pub fn request_redownload(all: bool, area: Option<i64>) -> Result<()> {
    let areas = if all {
        let mut server_conn = db::connect_to_server_db()?;
        Area::all(&mut server_conn)?
            .iter()
            .filter(|a| a.state != AreaState::Frozen)
            .map(|a| a.osm_id)
            .collect()
    } else {
        vec![area.unwrap()]
    };
    for area_id in areas {
        let mut stream = ChangesStream::new_from_env(area_id)?;
        println!("Processing area {area_id}");
        let removed = stream.trim_to_exact_length(0)?;
        println!("Removed {removed} changes from the stream.");
        stream.request_redownload()?;
        println!("The clients were notified about a redownload request.");
        println!("Success.");
    }
    Ok(())
}
