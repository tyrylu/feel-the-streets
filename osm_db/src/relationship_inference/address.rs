use crate::{AreaDatabase, Result, entity::Entity, entity_relationship::EntityRelationship, entity_relationship_kind::EntityRelationshipKind};

pub(crate) fn try_infer_address_for(entity: &mut    Entity, db: &AreaDatabase) -> Result<Vec<EntityRelationship>> {
    let mut res = vec![];
    // For all of these, computing an address relationship makes no sense - they already have it or do not specify an area or are usually too huge or do not have addresses.
    if !(entity.is_road_like() || entity.id.starts_with('r') || entity.discriminator == "Addressable" || !entity.value_of_field("address").is_null()) {
        let num_addressables = db.num_addressables_in(&entity.id)?;
        if  num_addressables == 1 { // We have a single address point in an entity - assume that the address applies to it and everything within it as well.
            let entities = db.get_basic_contained_entities_info(&entity.id)?;
            let addressable_info = entities.iter().find(|e| e.discriminator == "Addressable").unwrap();
            for entity in &entities {
                if entity.id == addressable_info.id {
                    continue;
                }
                res.push(EntityRelationship::new(entity.id.clone(), addressable_info.id.clone(), EntityRelationshipKind::Address));
            }
        }
        if num_addressables > 1 { // They belong all to the outer entity, but inferring internal relationships would be tricky - hopefully, we already inferred them or will in a short while.
for id in db.get_addressable_ids_in(&entity.id)? {
    res.push(EntityRelationship::new(entity.id.clone(), id, EntityRelationshipKind::Address));
}
        }
    }
        Ok(res)
}