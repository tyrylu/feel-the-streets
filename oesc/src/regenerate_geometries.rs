use anyhow::Result;
use osm_db::AreaDatabase;
use server::db;
use server::area::Area;

const AREA_ID_OFFSET: i64 = 3_600_000_000;

pub(crate) fn regenerate_area_geometries() -> Result<()> {
    let mut conn = db::connect_to_server_db()?;
    for mut area in Area::all(&mut conn)? {
        let area_db = AreaDatabase::open_existing(area.osm_id, true)?;
    let rel_id = format!("r{}", area.osm_id - AREA_ID_OFFSET);
    match area_db.get_entity_raw(&rel_id)? {
        Some(area_rel) => {
            area.geometry = Some(area_rel.geometry);
            area.save(&mut conn)?;
            println!("Updated area {} with geometry of length {}", area.osm_id, area.geometry.unwrap().len());
        },
        None => {
            println!("Area {} lacks an area object in the database.", area.osm_id);
        }
    }
        }
    Ok(())
}