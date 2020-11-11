use crate::entity_relationship_kind::EntityRelationshipKind;

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
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

#[derive(Clone, Debug, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub struct RootedEntityRelationship {
    pub child_id: String,
    pub kind: EntityRelationshipKind
}

impl RootedEntityRelationship {
    pub fn new(child_id: String, kind: EntityRelationshipKind) -> Self {
    RootedEntityRelationship{child_id, kind}
    }
}