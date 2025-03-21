use crate::entity_relationship_kind::EntityRelationshipKind;
use osm_api::SmolStr;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct EntityRelationship {
    pub parent_id: SmolStr,
    pub child_id: SmolStr,
    pub kind: EntityRelationshipKind,
}

impl EntityRelationship {
    pub fn new(parent_id: &str, child_id: &str, kind: EntityRelationshipKind) -> Self {
        EntityRelationship {
            parent_id: parent_id.into(),
            child_id: child_id.into(),
            kind,
        }
    }
}

#[derive(Clone, Debug, Hash, PartialEq, Eq, Serialize, Deserialize)]
pub struct RootedEntityRelationship {
    pub child_id: SmolStr,
    pub kind: EntityRelationshipKind,
}

impl RootedEntityRelationship {
    pub fn new(child_id: &str, kind: EntityRelationshipKind) -> Self {
        RootedEntityRelationship {
            child_id: child_id.into(),
            kind,
        }
    }
}
