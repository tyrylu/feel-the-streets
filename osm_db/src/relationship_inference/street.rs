use crate::entity::Entity;
use crate::entity_relationship::EntityRelationship;
use crate::AreaDatabase;
use crate::Result;
use crate::{entities_query::EntitiesQuery, entity_relationship_kind::EntityRelationshipKind};
use std::collections::HashMap;

fn get_association_for_street(
    street_name: &str,
    target_id: &str,
    cache: &mut HashMap<String, Option<String>>,
    db: &AreaDatabase,
) -> Result<Option<EntityRelationship>> {
    if let Some(record) = cache.get(street_name) {
        if let Some(id) = record {
            return Ok(Some(EntityRelationship::new(
                id,
                target_id,
                EntityRelationshipKind::Street,
            )));
        } else {
            return Ok(None);
        }
    }
    let roads = db.get_road_ids_with_name(street_name, target_id)?;
    if roads.is_empty() {
        warn!(
            "An address tag references the street {}, but no such street exists in the database.",
            street_name
        );
        cache.insert(street_name.to_string(), None);
        Ok(None)
    } else {
        if roads.len() == 1 {
            cache.insert(street_name.to_string(), Some(roads[0].clone()));
        }
        Ok(Some(EntityRelationship::new(
            &roads[0],
            target_id,
            EntityRelationshipKind::Street,
        )))
    }
}

fn try_infer_street_for_non_addressable(
    entity: &mut Entity,
    db: &AreaDatabase,
    mut cache: &mut HashMap<String, Option<String>>,
) -> Result<Option<EntityRelationship>> {
    try_infer_street_from_address_relationship(entity, db, &mut cache)
}

fn try_infer_street_from_address_relationship(
    entity: &Entity,
    db: &AreaDatabase,
    mut cache: &mut HashMap<String, Option<String>>,
) -> Result<Option<EntityRelationship>> {
    let mut query = EntitiesQuery::default();
    query.set_parent_id(entity.id.to_string());
    query.set_relationship_kind(EntityRelationshipKind::Address);
    let mut streets = vec![];
    let mut addressables = db.get_entities(&query)?;
    for addressable in &mut addressables {
        debug!(
            "Getting street from {:?}",
            addressable.value_of_field("address")
        );
        let maybe_addr_object = addressable.value_of_field("address");
        if let Some(addr) = maybe_addr_object.as_object() {
            if let Some(street) = addr.get("street") {
                let street_str = street.as_str().expect("Street was not a string");
                streets.push(street_str);
            } else {
                warn!("Address object is missing a street, it is: {:?}", addr);
            }
        } else {
            warn!(
                "Address property was not an object, it was {} instead.",
                maybe_addr_object
            );
        }
    }
    if !streets.is_empty() && streets.windows(2).all(|w| w[0] == w[1]) {
        get_association_for_street(streets[0], &entity.id, &mut cache, db)
    } else {
        Ok(None)
    }
}

pub(crate) fn try_infer_street_for(
    mut entity: &mut Entity,
    db: &AreaDatabase,
    mut cache: &mut HashMap<String, Option<String>>,
) -> Result<Option<EntityRelationship>> {
    let addr_field = entity.value_of_field("address").clone();
    if addr_field.is_null() | !addr_field.is_object() {
        return try_infer_street_for_non_addressable(&mut entity, db, &mut cache);
    }
    if let Some(street) = addr_field
        .as_object()
        .expect("Street should be always an object")
        .get("street")
    {
        let street_str = street.as_str().expect("Street should be a string.");
        return get_association_for_street(street_str, &entity.id, &mut cache, db);
    }
    // Try inferring for entity which had an address without a street
    try_infer_street_for_non_addressable(&mut entity, db, &mut cache)
}
