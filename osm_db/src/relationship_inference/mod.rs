use crate::area_db::{AreaDatabase, row_to_entity};
use crate::entity_relationship::EntityRelationship;
use crate::entities_query::EntitiesQuery;
use crate::entities_query_executor::EntitiesQueryExecutor;
use crate::Result;

mod street;

pub fn infer_additional_relationships_for(db: &AreaDatabase) -> Result<Vec<EntityRelationship>> {
    let query = EntitiesQuery::default();
    let mut executor = EntitiesQueryExecutor::new(&query);
        let rows = executor.prepare_execute(&db)?;
        let results = rows.mapped(row_to_entity).map(|e| e.expect("Failed to retrieve entity"));
        let mut relationships = 0;
        for mut entity in results {
            if let Some(relationship) = street::try_infer_street_for(&mut entity, &db)? {
                relationships += 1;
            }
        }
        info!("Inferred {} street relationships.", relationships);
    Ok(vec![])
}