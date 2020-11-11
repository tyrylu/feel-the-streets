use crate::{AreaDatabase, Result, entity::Entity, entity_relationship::EntityRelationship, entity_relationship_kind::EntityRelationshipKind};

pub(crate) fn try_infer_address_for(entity: &mut    Entity, db: &AreaDatabase) -> Result<Vec<EntityRelationship>> {
    let mut res = vec![];
    // For all of these, computing an address relationship makes no sense - they already have it or do not specify an area or are usually too huge or do not have addresses.
    if !(entity.is_road_like() || entity.id.starts_with('r') || entity.discriminator == "Addressable" || !entity.value_of_field("address").is_null()) {
        let addressable_ids = db.get_addressable_ids_in(&entity.id, true)?;
        if addressable_ids.len() == 1 { // We have a single address point in an entity - assume that the address applies to it and everything within it as well.
            let entity_ids = db.get_contained_entity_ids(&entity.id)?;
            for entity_id in &entity_ids {
                if *entity_id == addressable_ids[0] {
                    continue;
                }
                res.push(EntityRelationship::new(entity_id.clone(), addressable_ids[0].clone(), EntityRelationshipKind::Address));
            }
        }
        if addressable_ids.len() > 1 { // They belong all to the outer entity, but inferring internal relationships would be tricky - hopefully, we already inferred them or will in a short while.
for id in addressable_ids {
    res.push(EntityRelationship::new(entity.id.clone(), id, EntityRelationshipKind::Address));
}
        }
    }
        Ok(res)
}