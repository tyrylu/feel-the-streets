use crate:entity_relationship_kind::EntityRelationshipKind;

pub struct EntityRelationship {
    pub parent_id: String,
    pub child_id: string,
    pub kind: EntityRelationshipKind
}