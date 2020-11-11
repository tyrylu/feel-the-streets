use crate::entity_relationship::RootedEntityRelationship;
use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum EntryChange {
    Create {
        key: String,
        value: Value,
    },
    Update {
        key: String,
        old_value: Value,
        new_value: Value,
    },
    Remove {
        key: String,
    },
}

impl EntryChange {
    pub fn updating(key: &str, old_value: Value, new_value: Value) -> Self {
        EntryChange::Update {
            key: key.to_string(),
            old_value,
            new_value,
        }
    }
    pub fn creating(key: &str, value: Value) -> Self {
        EntryChange::Create {
            key: key.to_string(),
            value,
        }
    }
    pub fn removing(key: &str) -> Self {
        EntryChange::Remove {
            key: key.to_string(),
        }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum RelationshipChange {
    Add { value: RootedEntityRelationship },
    Remove { value: RootedEntityRelationship },
}

impl RelationshipChange {
    pub fn adding(value: RootedEntityRelationship) -> Self {
        RelationshipChange::Add { value }
    }

    pub fn removing(value: RootedEntityRelationship) -> Self {
        RelationshipChange::Remove { value }
    }
}

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum SemanticChange {
    RedownloadDatabase,
    Create {
        id: String,
        geometry: String,
        discriminator: String,
        data: String,
        effective_width: Option<f64>,
        entity_relationships: Vec<RootedEntityRelationship>,
    },
    Remove {
        osm_id: String,
    },
    Update {
        osm_id: String,
        property_changes: Vec<EntryChange>,
        data_changes: Vec<EntryChange>,
        relationship_changes: Vec<RelationshipChange>,
    },
}

impl SemanticChange {
    pub fn creating(
        id: String,
        geometry: Vec<u8>,
        discriminator: String,
        data: String,
        effective_width: Option<f64>,
        relationships: Vec<RootedEntityRelationship>,
    ) -> Self {
        SemanticChange::Create {
            geometry: base64::encode(&geometry),
            id,
            discriminator,
            data,
            effective_width,
            entity_relationships: relationships,
        }
    }
    pub fn removing(osm_id: &str) -> Self {
        SemanticChange::Remove {
            osm_id: osm_id.to_string(),
        }
    }

    pub fn updating(
        osm_id: &str,
        property_changes: Vec<EntryChange>,
        data_changes: Vec<EntryChange>,
        relationship_changes: Vec<RelationshipChange>,
    ) -> Self {
        SemanticChange::Update {
            property_changes,
            data_changes,
            relationship_changes,
            osm_id: osm_id.to_string(),
        }
    }

    pub fn add_rooted_relationship(&mut self, relationship: RootedEntityRelationship) {
        use SemanticChange::*;
        match self {
            Remove { .. } | RedownloadDatabase => {} // Adding a relationship to a removal change makes no sense, same for a redownload request.
            Create {
                entity_relationships,
                ..
            } => entity_relationships.push(relationship),
            Update {
                relationship_changes,
                ..
            } => relationship_changes.push(RelationshipChange::adding(relationship)),
        }
    }

    pub fn osm_id(&self) -> Option<&str> {
        use SemanticChange::*;
        match self {
            RedownloadDatabase => None,
            Create { id, .. } => Some(id),
            Update { osm_id, .. } => Some(osm_id),
            Remove { osm_id, .. } => Some(osm_id),
        }
    }

    pub fn is_remove(&self) -> bool {
        match self {
            SemanticChange::Remove { .. } => true,
            _ => false,
        }
    }

    pub fn is_create(&self) -> bool {
        match self {
            SemanticChange::Create { .. } => true,
            _ => false,
        }
    }

    pub fn is_update(&self) -> bool {
        match self {
            SemanticChange::Update { .. } => true,
            _ => false,
        }
    }

    pub fn add_relationship_change(&mut self, change: RelationshipChange) {
        match self {
            SemanticChange::Update {
                relationship_changes,
                ..
            } => relationship_changes.push(change),
            _ => {}
        }
    }
}
