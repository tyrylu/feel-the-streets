use anyhow::Result;
use diesel::{Connection, SqliteConnection};
use osm_db::area_db::AreaDatabase;
use osm_db::entities_query::EntitiesQuery;
use osm_db::entities_query_condition::{Condition, FieldCondition};
use osm_db::semantic_change::{EntryChange, SemanticChange};
use redis_api::ChangesStream;
use server::area::Area;

pub fn remove_field(entity: String, field: String, new_name: Option<String>) -> Result<()> {
    let server_conn = SqliteConnection::establish("server.db")?;
    for area in Area::all_updated(&server_conn)? {
        println!("Processing area {} (id {})...", area.name, area.osm_id);
        let mut area_db = AreaDatabase::open_existing(area.osm_id, true)?;
        let mut query = EntitiesQuery::default();
        query.set_included_discriminators(vec![entity.clone()]);
        query.add_condition(FieldCondition::new(field.clone(), Condition::IsNotNull));
        let mut changes = vec![];
        for mut entity in area_db.get_entities(&query)?.into_iter() {
            let val = entity.value_of_field(&field).clone();
            let mut entry_changes = vec![EntryChange::removing(&field)];
            if let Some(new_name) = &new_name {
                entry_changes.push(EntryChange::creating(new_name, val));
            }
            changes.push(SemanticChange::updating(
                entity
                    .value_of_field("osm_id")
                    .as_str()
                    .expect("OSM Id not a string?"),
                vec![],
                entry_changes,
                vec![],
            ));
        }
        if new_name.is_some() {
            println!(
                "Applying and publishing {} changes resulting from the rename...",
                changes.len()
            );
        } else {
            println!(
                "Applying and publishing {} changes resulting from the removal...",
                changes.len()
            );
        }
        area_db.begin()?;
        let mut stream = ChangesStream::new_from_env(area.osm_id)?;
        let mut batch = stream.begin_batch();
        for change in &changes {
            area_db.apply_change(change)?;
            batch.add_change(change)?;
        }
        area_db.commit()?;
        println!("Area processed successfully.");
    }
    println!("Cleaning up...");
    Ok(())
}
