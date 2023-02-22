use anyhow::Result;
use osm_db::area_db::AreaDatabase;
use osm_db::entities_query::EntitiesQuery;
use server::area::Area;
use server::db;
use std::collections::HashMap;

pub fn view_field_usage(entity: String, field: String) -> Result<()> {
    let mut server_conn = db::connect_to_server_db()?;
    let mut values = HashMap::new();
    let mut null_values = 0;
    let mut nonnull_values = 0;
    for area in Area::all(&mut server_conn)? {
        println!("Processing area {} (id {})...", area.name, area.osm_id);
        let area_db = AreaDatabase::open_existing(area.osm_id, true)?;
        let mut query = EntitiesQuery::default();
        query.set_included_discriminators(vec![entity.clone()]);
        for mut entity in area_db.get_entities(&query)?.into_iter() {
            let val = entity.value_of_field(&field);
            if val.is_null() {
                null_values += 1;
            } else {
                nonnull_values += 1;
                let val_str = val.to_string();
                *values.entry(val_str).or_insert(0) += 1;
            }
        }
        println!("Area processed successfully.");
    }
    println!(
        "{} entities had the field, {} did not. The entities had {} distinct values of the field.",
        nonnull_values,
        null_values,
        values.len()
    );
    println!("Values summary follows.");
    for (val, occurrences) in values.iter() {
        println!("{val} occurs {occurrences} times.");
    }
    Ok(())
}
