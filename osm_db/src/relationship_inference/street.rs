use crate::{entities_query::EntitiesQuery, entity_relationship_kind::EntityRelationshipKind};
use crate::entity_relationship::EntityRelationship;
use crate::entity::Entity;
use crate::Result;
use crate::AreaDatabase;
use std::collections::HashMap;

fn get_association_for_street(street_name: &str, target_id: &str, cache: &mut HashMap<String, String>, db: &AreaDatabase) -> Result<Option<EntityRelationship>> {
    if let Some(id) = cache.get(street_name) {
        return Ok(Some(EntityRelationship::new(id.clone(), target_id.to_string(), EntityRelationshipKind::Street)));
    }
let roads = db.get_road_ids_with_name(&street_name, target_id)?;
if roads.is_empty() {
            warn!("An address tag references the street {}, but no such street exists in the database.", street_name);
    return Ok(None);
}
else {
    if roads.len() == 1 {
        cache.insert(street_name.to_string(), roads[0].clone());
    }
    return Ok(Some(EntityRelationship::new(roads[0].clone(), target_id.to_string(), EntityRelationshipKind::Street)));
}
}

fn try_infer_street_for_non_addressable(entity: &mut Entity, db: &AreaDatabase, mut cache: &mut HashMap<String, String>) -> Result<Option<EntityRelationship>> {
try_infer_street_from_address_relationship(&entity, &db, &mut cache)
}

fn try_infer_street_from_address_relationship(entity: &Entity, db: &AreaDatabase, mut cache: &mut HashMap<String, String>) -> Result<Option<EntityRelationship>> {
    let mut query = EntitiesQuery::default();
    query.set_child_id(entity.id.clone());
    query.set_relationship_kind(EntityRelationshipKind::Address);
    let mut streets = vec![];
    let mut addressables = db.get_entities(&query)?;
    for addressable in &mut addressables {
        debug!("Getting street from {:?}", addressable.value_of_field("address"));
        let street_str = addressable.value_of_field("address").as_object().expect("Malformed address object").get("street").expect("Street disappeared?").as_str().expect("Street was not a string");
        streets.push(street_str);
    }
        if !streets.is_empty() && streets.windows(2).all(|w| w[0] == w[1]) {
            get_association_for_street(&streets[0], &entity.id, &mut cache, &db)
        }
else {
    Ok(None)
}     
}

pub(crate) fn try_infer_street_for(mut entity: &mut Entity, db: &AreaDatabase, mut cache: &mut HashMap<String, String>) -> Result<Option<EntityRelationship>> {
let addr_field = entity.value_of_field("address").clone();
if addr_field.is_null() {
    return try_infer_street_for_non_addressable(&mut entity, &db, &mut cache);
}
if let Some(street) = addr_field.as_object().expect("Street should be always an object").get("street") {
    let street_str = street.as_str().expect("Street should be a string.");
    return get_association_for_street(street_str, &entity.id, &mut cache, &db);
}
// Try inferring for entity which had an address without a street
try_infer_street_for_non_addressable(&mut entity, &db, &mut cache)
}