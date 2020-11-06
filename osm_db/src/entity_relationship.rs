use crate::entity_relationship_kind::EntityRelationshipKind;

pub struct EntityRelationship {
    pub parent_id: String,
    pub child_id: String,
    pub kind: EntityRelationshipKind
}

impl EntityRelationship {
    pub fn new(parent_id: String, child_id: String, kind: EntityRelationshipKind) -> Self {
    EntityRelationship{parent_id, child_id, kind}
    }
}