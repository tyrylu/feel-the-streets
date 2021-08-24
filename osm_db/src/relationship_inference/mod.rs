use crate::area_db::{row_to_entity, AreaDatabase};
use crate::entities_query::EntitiesQuery;
use crate::entities_query_executor::EntitiesQueryExecutor;
use crate::entity::Entity;
use crate::entity_relationship::EntityRelationship;
use crate::Result;
use std::collections::HashMap;
use log::{trace, info};

mod address;
mod street;

pub fn infer_additional_relationships_for_entity(
    mut entity: &mut Entity,
    db: &AreaDatabase,
    mut street_names_cache: &mut HashMap<String, Option<String>>,
) -> Result<Vec<EntityRelationship>> {
    trace!(
        "Inferring address relationships for {} {}",
        entity.discriminator,
        entity.id
    );
    let mut relationships = vec![];
    for relationship in address::try_infer_address_for(&mut entity, db)? {
        // Note that we must insert the address relationships there because otherwise we would not be able to use them when identifying the street relationships.
        db.insert_entity_relationship(&relationship)?;
        relationships.push(relationship);
    }
    if let Some(relationship) =
        street::try_infer_street_for(&mut entity, db, &mut street_names_cache)?
    {
        // And for consistency, we'll insert this one as well.
        db.insert_entity_relationship(&relationship)?;
        relationships.push(relationship);
    }
    Ok(relationships)
}

pub fn infer_additional_relationships_for(db: &AreaDatabase) -> Result<Vec<EntityRelationship>> {
    let query = EntitiesQuery::default();
    let mut executor = EntitiesQueryExecutor::new(&query);
    let rows = executor.prepare_execute(db)?;
    let results = rows
        .mapped(row_to_entity)
        .map(|e| e.expect("Failed to retrieve entity"));
    let mut street_names_cache = HashMap::new();
    let mut relationships = vec![];
    for mut entity in results {
        let mut new_relationships =
            infer_additional_relationships_for_entity(&mut entity, db, &mut street_names_cache)?;
        relationships.append(&mut new_relationships);
    }
    info!("Inferred {} relationships.", relationships.len());
    Ok(relationships)
}
