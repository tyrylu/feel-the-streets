use crate::entity_relationship_kind::EntityRelationshipKind;
use crate::entity_relationship::EntityRelationship;
use crate::entity::Entity;
use crate::Result;
use crate::AreaDatabase;
use std::collections::HashMap;

pub(crate) fn try_infer_street_for(entity: &mut Entity, db: &AreaDatabase, cache: &mut HashMap<String, String>) -> Result<Option<EntityRelationship>> {
let addr_field = entity.value_of_field("address").clone();
if addr_field.is_null() {
    return Ok(None);
}
if let Some(street) = addr_field.as_object().expect("Street should be always an object").get("street") {
    let street_str = street.as_str().expect("Street should be a string.");
    if let Some(id) = cache.get(street_str) {
        return Ok(Some(EntityRelationship::new(id.clone(), entity.id.clone(), EntityRelationshipKind::Street)));
    }
let roads = db.get_road_ids_with_name(&street_str, &entity.id)?;
if roads.len() == 0 {
            warn!("An address tag references the street {}, but no such street exists in the database.", street_str);
    return Ok(None);
}
else {
    if roads.len() == 1 {
        cache.insert(street_str.to_string(), roads[0].clone());
    }
    return Ok(Some(EntityRelationship::new(roads[0].clone(), entity.id.clone(), EntityRelationshipKind::Street)));
}
}
    Ok(None)
}