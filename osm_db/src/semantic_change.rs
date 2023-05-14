use crate::entity_relationship::RootedEntityRelationship;
use crate::Result;
use base64::prelude::*;
use once_cell::sync::Lazy;
use osm_api::SmolStr;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::sync::Mutex;
use zstd_util::ZstdContext;

static ZSTD_CONTEXT: Lazy<Mutex<ZstdContext>> = Lazy::new(|| {
    Mutex::new(ZstdContext::new(
        10,
        Some(include_bytes!("../../changes.dict")),
    ))
});

#[derive(Serialize, Deserialize, Debug, Clone)]
pub enum EntryChange {
    Create {
        key: SmolStr,
        value: Value,
    },
    Update {
        key: SmolStr,
        old_value: Value,
        new_value: Value,
    },
    Remove {
        key: SmolStr,
    },
}

impl EntryChange {
    pub fn updating(key: &str, old_value: Value, new_value: Value) -> Self {
        EntryChange::Update {
            key: SmolStr::new_inline(key),
            old_value,
            new_value,
        }
    }
    pub fn creating(key: &str, value: Value) -> Self {
        EntryChange::Create {
            key: SmolStr::new_inline(key),
            value,
        }
    }
    pub fn removing(key: &str) -> Self {
        EntryChange::Remove {
            key: SmolStr::new_inline(key),
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
    Create {
        id: SmolStr,
        geometry: String,
        discriminator: SmolStr,
        data: String,
        effective_width: Option<f64>,
        entity_relationships: Vec<RootedEntityRelationship>,
    },
    Remove {
        osm_id: SmolStr,
    },
    Update {
        osm_id: SmolStr,
        property_changes: Vec<EntryChange>,
        data_changes: Vec<EntryChange>,
        relationship_changes: Vec<RelationshipChange>,
    },
}

impl SemanticChange {
    pub fn creating(
        id: &str,
        geometry: Vec<u8>,
        discriminator: &str,
        data: String,
        effective_width: Option<f64>,
        relationships: Vec<RootedEntityRelationship>,
    ) -> Self {
        SemanticChange::Create {
            geometry: BASE64_STANDARD.encode(geometry),
            id: SmolStr::new_inline(id),
            discriminator: SmolStr::new_inline(discriminator),
            data,
            effective_width,
            entity_relationships: relationships,
        }
    }
    pub fn removing(osm_id: &str) -> Self {
        SemanticChange::Remove {
            osm_id: SmolStr::new_inline(osm_id),
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
            osm_id: SmolStr::new_inline(osm_id),
        }
    }

    pub fn add_rooted_relationship(&mut self, relationship: RootedEntityRelationship) {
        use SemanticChange::*;
        match self {
            Remove { .. } => {} // Adding a relationship to a removal change makes no sense, same for a redownload request.
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

    pub fn osm_id(&self) -> &str {
        use SemanticChange::*;
        match self {
            Create { id, .. } => id,
            Update { osm_id, .. } => osm_id,
            Remove { osm_id, .. } => osm_id,
        }
    }

    pub fn is_remove(&self) -> bool {
        matches!(self, SemanticChange::Remove { .. })
    }

    pub fn is_create(&self) -> bool {
        matches!(self, SemanticChange::Create { .. })
    }

    pub fn is_update(&self) -> bool {
        matches!(self, SemanticChange::Update { .. })
    }

    pub fn add_relationship_change(&mut self, change: RelationshipChange) {
        if let SemanticChange::Update {
            relationship_changes,
            ..
        } = self
        {
            relationship_changes.push(change)
        }
    }

    pub fn serialize(&self) -> Result<Vec<u8>> {
        let encoded = serde_json::to_string(&self)?;
        Ok(ZSTD_CONTEXT
            .lock()
            .unwrap()
            .compress(&encoded.into_bytes())?)
    }

    pub fn from_serialized(data: &[u8]) -> Result<Self> {
        let decompressed = ZSTD_CONTEXT.lock().unwrap().decompress(data)?;
        Ok(serde_json::from_slice(&decompressed)?)
    }
}
