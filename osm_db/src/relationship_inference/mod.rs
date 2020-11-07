use crate::area_db::{AreaDatabase, row_to_entity};
use crate::entity_relationship::EntityRelationship;
use crate::entities_query::EntitiesQuery;
use crate::entities_query_executor::EntitiesQueryExecutor;
use crate::Result;
use std::collections::HashMap;

mod address;
mod street;

pub fn infer_additional_relationships_for(db: &AreaDatabase) -> Result<Vec<EntityRelationship>> {
    let query = EntitiesQuery::default();
    let mut executor = EntitiesQueryExecutor::new(&query);
        let rows = executor.prepare_execute(&db)?;
        let results = rows.mapped(row_to_entity).map(|e| e.expect("Failed to retrieve entity"));
        let mut street_relationships = 0;
        let mut address_relationships = 0;
        let mut street_names_cache = HashMap::new();
        let mut relationships = vec![];
        for mut entity in results {
            for relationship in address::try_infer_address_for(&entity, &db)? {
                relationships.push(relationship);
address_relationships += 1;
            }
            if let Some(relationship) = street::try_infer_street_for(&mut entity, &db, &mut street_names_cache)? {
                street_relationships += 1;
                relationships.push(relationship);
            }
        }
        info!("Inferred {} address relationnships and {} street relationships.", address_relationships, street_relationships);
    Ok(relationships)
}